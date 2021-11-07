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
import re

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



def test__get_git_info_string(monkeypatch):
    """
    Tests the `_get_git_info_string()` method.
    """
    def mock__get_git_commit_hash():
        """
        Return a uniquely identifiable string for this test.
        """
        return 'hash'

    def mock__get_git_branch_code():
        """
        Return a uniquely identifiable string for this test.
        """
        return 'branch'

    def mock__get_git_status_code():
        """
        Return a uniquely identifiable string for this test.
        """
        return 'status'

    monkeypatch.setattr(version, '_get_git_commit_hash',
            mock__get_git_commit_hash)
    monkeypatch.setattr(version, '_get_git_branch_code',
            mock__get_git_branch_code)
    monkeypatch.setattr(version, '_get_git_status_code',
            mock__get_git_status_code)

    assert version._get_git_info_string() == 'hash-branch-status'

    def mock__get_git_status_code__empty():
        """
        Return an emtpy status code
        """
        return ''

    monkeypatch.setattr(version, '_get_git_status_code',
            mock__get_git_status_code__empty)

    assert version._get_git_info_string() == 'hash-branch'



def test__get_git_commit_hash__real():
    """
    Tests the `_get_git_commit_hash()` method.

    This will test to make sure it can really get a commit hash.  It may vary
    from test to test, but since this should always be run in a git repo, it
    should pass.
    """
    git_commit_hash = version._get_git_commit_hash()
    assert re.match(r'^[0-9a-f]{7}$', git_commit_hash) is not None



def test__get_git_branch_code__real():
    """
    Tests the `_get_git_branch_code()` method.

    This will test to make sure it can really get a branch code.  It may vary
    from test to test, but since this should always be run in a git repo, it
    should pass.
    """
    git_branch_code = version._get_git_branch_code()
    assert any(git_branch_code == c for c in ['b', 'd', 'h', 's']) is True



def test__get_git_status_code__real():
    """
    Tests the `_get_git_status_code()` method.

    This will test to make sure it can really get a status code.  It may vary
    from test to test, but since this should always be run in a git repo, it
    should pass.
    """
    git_status_code = version._get_git_status_code()
    assert re.match(r'^[ACDMRUiu]*-[ACDMRUiu]*$', git_status_code) is not None \
            or git_status_code == ''
