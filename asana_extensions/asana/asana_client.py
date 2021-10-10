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



def _get_client():
    """
    Ensures the client is initialized and ready for use.

    Returns:
      (Client): Asana client, either the previously cached one or a new one.
    """
    if not hasattr(_get_client, 'client') or _get_client.client is None:
        parser = config.read_conf_file('.secrets.conf')
        pat = parser['asana']['personal access token']
        _get_client.client = asana.Client.access_token(pat)
    return _get_client.client
