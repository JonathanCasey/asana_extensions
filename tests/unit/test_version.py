#!/usr/bin/env python3
"""
Tests the asana_extensions.version functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import datetime as dt

from asana_extensions import version



def test_get_full_version_string():
    """
    Tests the `get_full_version_string()` method.
    """
    full_ver_str = version.get_full_version_string()
    full_ver_str_parts = full_ver_str.split('_')
    assert 'v' + version._VERSION == full_ver_str_parts[0]
    dt.datetime.strptime(full_ver_str_parts[1], '%Y%m%d-%H%M%S')
    assert version._get_git_info_string() == full_ver_str_parts[2]
