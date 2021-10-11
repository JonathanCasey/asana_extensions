#!/usr/bin/env python3
"""
Asana client wrapper.  This will manage the client connection state and expose
methods to be called for specific purposes.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

import asana

from asana_extensions.general import config



logger = logging.getLogger(__name__)



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



def _get_me():
    """
    Gets the data for 'me' (self) user.

    At this time, only here for testing API connection, as it is the most basic
    way to test API access is working.

    Returns:
      ({str: str/int/dict/etc}): The data for the 'me' (self) user.  See
        full schema here: https://developers.asana.com/docs/user

    Raises:
      (asana.error.NoAuthorizationError): Personal access token was missing or
        invalid.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    client = _get_client()
    try:
        return client.users.me()
    except asana.error.NoAuthorizationError as ex:
        logger.error('Failed to access API in _get_me() - Not Authorized:'
                + f' {ex}')
        raise



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
      found_gid (int): The only gid that matches this workspace name.

    Raises:
      (asana.error.NoAuthorizationError): Personal access token was missing or
        invalid.
      (DataNotFoundError): Workspace name not found at all.
      (DuplicateNameError): Workspace name found more than once with different
        gids.
      (MismatchedDataError): Workspace name found, but gid found did not match
        the non-None gid provided.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    client = _get_client()
    try:
        workspaces = client.workspaces.get_workspaces()
    except asana.error.NoAuthorizationError as ex:
        logger.error('Failed to access API in get_workspace_gid_from_name() -'
                + f' Not Authorized: {ex}')
        raise

    found_gid = None
    for workspace in workspaces:
        if workspace['resource_type'] != 'workspace':
            continue
        if workspace['name'] == ws_name:
            if found_gid is None:
                found_gid = workspace['gid']
            else:
                raise DuplicateNameError(f'The workspace "{ws_name}" matched at'
                        + f' least 2 gids: {found_gid} and {workspace["gid"]}')

    if found_gid is None:
        raise DataNotFoundError(f'The workspace "{ws_name}" was not found')
    if ws_gid is not None and found_gid != ws_gid:
        raise MismatchedDataError(f'The workspace "{ws_name}" found gid'
                + f' {found_gid}, but expected gid {ws_gid}')
    if ws_gid is None:
        logger.info(f'GID of workspace "{ws_name}" is {found_gid}')
    return found_gid
