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

  _PROJECT_TEMPLATE (Template): The name format to be used for test projects
    created in the test workspace for unit testing.  IDs will be substituted as
    needed for testing.  This will be created and deleted as needed during unit
    testing.

  _SECTION_TEMPLATE (Template): The name format to be used for test sections
    created in the test workspace for unit testing.  IDs will be substituted as
    needed for testing.  This will be created and deleted as needed during unit
    testing.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from string import Template



_WORKSPACE = 'TEST Asana Extensions'

_PROJECT_TEMPLATE = Template('TEST Project $pid')

_SECTION_TEMPLATE = Template('TEST Section $sid')
