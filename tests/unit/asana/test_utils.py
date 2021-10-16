#!/usr/bin/env python3
"""
Tests the asana_extensions.asana.utils functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""

from asana_extensions.asana import client as aclient
from asana_extensions.asana import utils as autils



def test_get_net_include_section_gids(monkeypatch):
    """
    Tests the `get_net_include_section_gids()` method.
    """

    def mock_get_section_gids_in_project_or_utl(
            proj_or_utl_gid):                  # pylint: disable=unused-argument
        """
        Returns a list of fake gids that can be used for testing.
        """
        return [1, 2, 3, 4, 5, 6]


    def mock_get_section_gid_from_name(
            proj_or_utl_gid, sect_name,        # pylint: disable=unused-argument
            sect_gid=None):                    # pylint: disable=unused-argument
        """
        Makes a fake map of names to gids, then returns the gid for a given
        name.
        """
        names_to_gids = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
        }
        return names_to_gids[sect_name]


    monkeypatch.setattr(aclient, 'get_section_gids_in_project_or_utl',
            mock_get_section_gids_in_project_or_utl)
    monkeypatch.setattr(aclient, 'get_section_gid_from_name',
            mock_get_section_gid_from_name)

    assert autils.get_net_include_section_gids(0) == {1, 2, 3, 4, 5, 6}
