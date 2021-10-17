#!/usr/bin/env python3
"""
Asana client wrapper.  This will manage the client connection state and expose
methods to be called for specific purposes.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from functools import wraps
import logging

import asana

from asana_extensions.general import config



logger = logging.getLogger(__name__)
logging.captureWarnings(True)



class ClientCreationError(Exception):
    """
    Raised when the client fails to be created for any reason.
    """

class DataNotFoundError(Exception):
    """
    Raised when the requested data is not found as expected.
    """

class DuplicateNameError(Exception):
    """
    Raised when a duplicate name is detected that cannot be resolved.
    """

class MismatchedDataError(Exception):
    """
    Raised when there is a mismatch in data between provided and found.  For
    example, a name and gid may be provided, but API shows a different gid.
    """



def asana_error_handler(f):
    """
    Decorator that handles all `AsanaError`s that can occur.  Intended to be
    used to wrap all methods here that are wrappers themselves for API calls.
    This assumes those methods are not handling the errors; but they always
    have the option to add a try/except to catch any specific errors and handle
    them differently.

    Use this with @asana_error_handler prior to function def.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        """
        Wrapping code to execute when function f is called, passing thru any/all
        args.
        """
        try:
            return f(*args, **kwargs)
        except asana.error.AsanaError as ex:
            logger.error(f'API query failed in {f.__module__}.{f.__name__}():'
                    + f' [{ex.status}] {ex.message}')
            raise

    wrapper._is_wrapped_by_asana_error_handler = True #pylint: disable=protected-access
    return wrapper



def _get_client():
    """
    Ensures the client is initialized and ready for use.

    Returns:
      (Client): Asana client, either the previously cached one or a new one.

    Raises:
      (ClientCreationError): Failed to create client for any reason.
    """
    if not hasattr(_get_client, 'client') or _get_client.client is None:
        try:
            parser = config.read_conf_file('.secrets.conf')
            pat = parser['asana']['personal access token']
            _get_client.client = asana.Client.access_token(pat)
        except KeyError as ex:
            raise ClientCreationError('Could not create client - Could not find'
                    + f' necessary section/key in .secrets.conf: {ex}') from ex
    return _get_client.client



@asana_error_handler
def _get_me():
    """
    Gets the data for 'me' (self) user.

    At this time, only here for testing API connection, as it is the most basic
    way to test API access is working.

    Returns:
      ({str: str/int/dict/etc}): The data for the 'me' (self) user.  See
        full schema here: https://developers.asana.com/docs/user

    Raises:
      (asana.error.AsanaError): Any errors from the API.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    client = _get_client()
    return client.users.me()



def _find_gid_from_name(data, resource_type, name, expected_gid=None):
    """
    This finds the gid from the provided data based on the provided name.  It
    will confirm the name is unique.  If a gid is provided, it will confirm it
    also matches.  This only checks the resource type provided.

    This works for data structures that fit the gid/name/resource_type key
    combo.

    Args:
      data (generator of {str: str/int/etc}): The data from the API.  Iterating
        it should result in items with gid/name/resource_type keys.
      resource_type (str): The resource type to match in the data.
      name (str): The name of the item to retrieve.
      expected_gid (int or None): Over-defines search.  The GID that should
        match the name.  Can be omitted if only using name.  Useful to confirm
        gid and name match.

    Returns:
      found_gid (int): The only gid that matches this name for this resource
        type in the provided data.

    Raises:
      (DataNotFoundError): Name not found at all.
      (DuplicateNameError): Name found more than once with different gids.
      (MismatchedDataError): Name found, but gid found did not match the
        non-None gid provided.
    """
    found_gid = None
    for entry in data:
        if entry['resource_type'] != resource_type:
            continue
        if entry['name'] == name:
            if found_gid is None:
                found_gid = entry['gid']
            else:
                raise DuplicateNameError(f'The {resource_type} "{name}"'
                        + f' matched at least 2 gids: {found_gid} and'
                        + f' {entry["gid"]}')

    if found_gid is None:
        raise DataNotFoundError(f'The {resource_type} "{name}" was not found')
    if expected_gid is not None and found_gid != expected_gid:
        raise MismatchedDataError(f'The {resource_type} "{name}" found gid'
                + f' {found_gid}, but expected gid {expected_gid}')
    if expected_gid is None:
        logger.info(f'GID of {resource_type} "{name}" is {found_gid}')
    return found_gid



def get_workspace_gid_from_name(ws_name, ws_gid=None):
    """
    This will get the workspace gid from the name.  It will confirm the name is
    unique.  If a gid is provided, it will confirm it also matches.  This only
    checked workspaces, not organizations.

    Args:
      ws_name (str): The name of the workspace to retrieve.
      ws_gid (int): Over-defines search.  The GID that should match the
        workspace name.  Can be omitted if only using name.  Useful to confirm
        gid and name match.

    Returns:
      (int): The only gid that matches this workspace name.

    Raises:
      (asana.error.NoAuthorizationError): Personal access token was missing or
        invalid.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    client = _get_client()
    try:
        workspaces = client.workspaces.get_workspaces()
    except asana.error.NoAuthorizationError as ex:
        logger.error('Failed to access API in get_workspace_gid_from_name() -'
                + f' Not Authorized: {ex}')
        raise

    return _find_gid_from_name(workspaces, 'workspace', ws_name, ws_gid)



def get_project_gid_from_name(ws_gid, proj_name, proj_gid=None, archived=False):
    """
    This will get the project gid from the name.  It will confirm the name is
    unique.  If a gid is provided, it will confirm it also matches.

    Args:
      ws_gid (int): The gid of the workspace for which to get this project.
      proj_name (str): The name of the project to retrieve.
      proj_gid (int): Over-defines search.  The GID that should match the
        project name.  Can be omitted if only using name.  Useful to confirm
        gid and name match.
      archived (bool or None): Whether or not to include archived projects.  If
        None, will include both.

    Returns:
      (int): The only gid that matches this project name.

    Raises:
      (asana.error.NoAuthorizationError): Personal access token was missing or
        invalid.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    params = {
        'workspace': ws_gid,
    }
    if archived is not None:
        params['archived'] = archived

    client = _get_client()
    try:
        projects = client.projects.get_projects(params)
    except asana.error.NoAuthorizationError as ex:
        logger.error('Failed to access API in get_project_gid_from_name() -'
                + f' Not Authorized: {ex}')
        raise

    return _find_gid_from_name(projects, 'project', proj_name, proj_gid)



def get_section_gid_from_name(proj_or_utl_gid, sect_name, sect_gid=None):
    """
    This will get the section gid from the name.  It will confirm the name is
    unique.  If a gid is provided, it will confirm it also matches.

    Args:
      proj_or_utl_gid (int): The gid of the project for which to get sections.
        Through empirical testing and noted as a 'trick' on dev forums, the
        user task list gid (not 'me') can be used to get the sections of that.
      sect_name (str): The name of the section to retrieve.
      sect_gid (int): Over-defines search.  The GID that should match the
        section name.  Can be omitted if only using name.  Useful to confirm
        gid and name match.

    Returns:
      (int): The only gid that matches this section name.

    Raises:
      (asana.error.NoAuthorizationError): Personal access token was missing or
        invalid.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    client = _get_client()
    try:
        sections = client.sections.get_sections_for_project(proj_or_utl_gid)
    except asana.error.NoAuthorizationError as ex:
        logger.error('Failed to access API in get_section_gid_from_name() -'
                + f' Not Authorized: {ex}')
        raise

    return _find_gid_from_name(sections, 'section', sect_name, sect_gid)



def get_user_task_list_gid(workspace_gid, is_me=False, user_gid=None):
    """
    Gets the "project ID" for the user task list, either by "me" or a specific
    user ID.

    Args:
      workspace_gid (int): The gid of the workspace for which to get the user's
        task list.
      is_me (bool): Set to true if getting the user task list for "me".  Cannot
        provide user_gid if using this.
      user_gid (int or None): Set to the integer of the user gid for the user
        task list to get.  Cannot provide is_me if using this.

    Returns:
      (int): The gid of the user task list for the provided user.

    Raises:
      (AssertionError): Invalid data.
      (asana.error.NoAuthorizationError): Personal access token was missing or
        invalid.
      (asana.error.NotFoundError): Invalid/inaccessible user gid provided.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    assert is_me ^ (user_gid is not None), 'Must provide `is_me` or' \
            + ' `user_gid`, but not both.'

    if is_me:
        # From API docs, access is equivalent subbing 'me' in for gid
        user_gid = 'me'
    params = {
        'workspace': workspace_gid,
    }

    client = _get_client()
    try:
        utl_data = client.user_task_lists.get_user_task_list_for_user(
                str(user_gid), params)
    except asana.error.NoAuthorizationError as ex:
        logger.error('Failed to access API in get_user_task_list_gid() -'
                + f' Not Authorized: {ex}')
        raise
    except asana.error.NotFoundError as ex:
        logger.error('Could not find requested data'
                + f' in get_user_task_list_gid(): {ex}')
        raise

    return int(utl_data['gid'])



def get_section_gids_in_project_or_utl(proj_or_utl_gid):
    """
    This gets the list of section gids in a project or user task list.

    Args:
      proj_or_utl_gid (int): The gid of the project for which to get sections.
        Through empirical testing and noted as a 'trick' on dev forums, the
        user task list gid (not 'me') can be used to get the sections of that.

    Returns:
      ([int]): The list of gids of sections in the given project or user task
        list.

    Raises:
      (asana.error.NoAuthorizationError): Personal access token was missing or
        invalid.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    client = _get_client()
    try:
        sections = client.sections.get_sections_for_project(proj_or_utl_gid)
    except asana.error.NoAuthorizationError as ex:
        logger.error('Failed to access API in'
                + ' get_section_gids_in_project_or_utl() -'
                + f' Not Authorized: {ex}')
        raise

    return [int(s['gid']) for s in sections]
