#!/usr/bin/env python3
"""
Asana client wrapper.  This will manage the client connection state and expose
methods to be called for specific

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
    Gets the data for 'me' (self).

    At this time, only here for testing API connection, as it is the most basic
    way to test API access is working.

    Returns:
      ({str: str/int/dict/etc}): The data for the 'me' (self) user.  See
        full schema here: https://developers.asana.com/docs/user

    Raises:
      (asana.error.NoAuthorizationError):
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    client = _get_client()
    try:
        return client.users.me()
    except asana.error.NoAuthorizationError as ex:
        logger.error('Failed to access API in _get_me() - Not Authorized:'
                + f' {ex}')
        raise
