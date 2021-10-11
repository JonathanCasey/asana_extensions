#!/usr/bin/env python3
"""
Data to be used for testing purposes only.  These are the workspaces and such
that will be used on the actual asana account provided by the access token.
There should not be any collisions, but always good to double check!

Module Attributes:
  _WORKSPACE (str): The name of the workspace that will be used for unit
    testing.  This must be created on the asana account associated with the
    personal access token being used for testing (in `.secrets.conf`) prior to
    running tests.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""



_WORKSPACE = 'TEST Asana Extensions'
