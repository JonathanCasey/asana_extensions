#!/usr/bin/env python3
"""
Asana utilities.  These are logic and other helper pieces that sit on top of the
client layer, using that data from the API to further manipulate data for
specific purposes.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from asana_extensions.asana import client as aclient



logger = logging.getLogger(__name__)



class DataConflictError(Exception):
    """
    Raised when there is a conflicting combination of data, such as data that is
    explicitly specified to be included and excluded at the same time.
    """



class DataMissingError(Exception):
    """
    Raised when there is data that is explicitly specified and expected to
    exist but it ultimately does not exist; and this data being missing is
    likely a critical error.
    """



def get_net_include_section_gids(              # pylint: disable=too-many-locals
        proj_or_utl_gid,
        include_sect_names=None, include_sect_gids=None,
        exclude_sect_names=None, exclude_sect_gids=None,
        default_to_include=True):
    """
    Gets the filterd list of section gids, providing only the net included ones.
    This will convert all names to gids and look at the resulting sets of
    included and exclude gids as compared to all section gids in the project or
    UTL.  This does not do anything special for matches or mismatches between
    names and gids within includes or within excludes; it simply takes the union
    of them to form a combined set.

    Any section that is explicitly both included and excluded will raise an
    error.

    The default behavior when no includes or excludes are provided can be
    specified, though providing any explicit includes will effectively override
    this behavior to default to exclude.

    Args:
      proj_or_utl_gid (int): The gid of the project for which to get sections.
        Through empirical testing and noted as a 'trick' on dev forums, the
        user task list gid (not 'me') can be used to get the sections of that.
      include_sect_names ([str] or None): The list of section names that will be
        explicitly included.
      include_sect_gids ([int] or None): The list of section gids that will be
        explicitly included.
      exclude_sect_names ([str] or None): The list of section names that will be
        explicitly excluded.
      exclude_sect_gids ([int] or None): The list of section gids that will be
        explicitly excluded.
      default_to_include (bool): The default behavior, such as when all include
        and exclude args are None.

    Returns:
      ({int}): The resulting set of section gids to include from the project.

    Raises:
      (DataConflictError): Raised if any gid (or gid derived from name) is
        explicitly both included and excluded.
      (DataMissingError): Raised if any gid (or gid derived from name) is
        explicitly included but is missing from the project.

      This will pass up unhandled client exceptions.
    """
    include_sect_names = include_sect_names or []
    include_sect_gids = include_sect_gids or []
    exclude_sect_names = exclude_sect_names or []
    exclude_sect_gids = exclude_sect_gids or []

    project_section_gids = set(aclient.get_section_gids_in_project_or_utl(
            proj_or_utl_gid))

    include_sect_gids_from_names = {aclient.get_section_gid_from_name(
            proj_or_utl_gid, s): s for s in include_sect_names}
    exclude_sect_gids_from_names = {aclient.get_section_gid_from_name(
            proj_or_utl_gid, s): s for s in exclude_sect_names}

    include_gids = set(include_sect_gids_from_names) | set(include_sect_gids)
    exclude_gids = set(exclude_sect_gids_from_names) | set(exclude_sect_gids)
    gids_to_names = {
        **include_sect_gids_from_names,
        **exclude_sect_gids_from_names,
    }

    if include_gids - project_section_gids:
        missing_gids = [str(g) for g in include_gids - project_section_gids]
        missing_names = [gids_to_names[int(g)] for g in missing_gids
                if int(g) in gids_to_names]
        err_msg = 'Section names/gids explicitly included are missing from' \
                + ' project/user task list.'
        err_msg += ' Check gids (some may not be explicitly in list if' \
                + f' provided by name): {", ".join(missing_gids)}.'
        if missing_names:
            err_msg += f' Also check names: `{"`, `".join(missing_names)}`.'
        raise DataMissingError(err_msg)

    if exclude_gids - project_section_gids:
        missing_gids = [str(g) for g in exclude_gids - project_section_gids]
        missing_names = [gids_to_names[int(g)] for g in missing_gids
                if int(g) in gids_to_names]
        warn_msg = 'Section names/gids explicitly excluded are missing from' \
                + ' project/user task list. This may be unintentional.'
        warn_msg += ' Check gids (some may not be explicitly in list if' \
                + f' provided by name): {", ".join(missing_gids)}.'
        if missing_names:
            warn_msg += f' Also check names: `{"`, `".join(missing_names)}`.'
        logger.warning(warn_msg)

    if include_gids & exclude_gids:
        conflicting_gids = [str(g) for g in include_gids & exclude_gids]
        conflicting_names = [gids_to_names[int(g)] for g in conflicting_gids
                if int(g) in gids_to_names]
        err_msg = 'Explicit section names/gids cannot be simultaneously' \
                + ' included and excluded.'
        err_msg += ' Check gids (some may not be explicitly in list if' \
                + f' provided by name): {", ".join(conflicting_gids)}.'
        if conflicting_names:
            err_msg += f' Also check names: `{"`, `".join(conflicting_names)}`.'
        raise DataConflictError(err_msg)

    if not default_to_include or (default_to_include and include_gids):
        return include_gids

    return project_section_gids - exclude_gids
