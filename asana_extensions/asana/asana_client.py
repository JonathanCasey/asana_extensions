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



_client = None



def _ensure_client_ready():
    """
    Ensures the client is initialized and ready for use.

    Sets the module's client attribute.
    """
    global _client
    if _client is None:
        parser = config.read_conf_file('.secrets.conf')
        pat = parser['asana']['personal access token']
        _client = asana.Client.access_token(pat)
