#!/usr/bin/env python3
"""
Tests the asana_extensions.__main__ functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

from asana_extensions import __main__



def test_modules():
    """
    Tests the "entire module".  This really just needs to import the module to
    make code coverage happy.  There is nothing in the project itself that is
    testable.
    """
    # Nothing to test -- just need a test so it tests the module import
    return
