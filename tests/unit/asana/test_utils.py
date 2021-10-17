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
import logging

import pytest

from asana_extensions.asana import client as aclient
from asana_extensions.asana import utils as autils



def test_get_net_include_section_gids(monkeypatch, caplog):
    """
    Tests the `get_net_include_section_gids()` method.
    """
    caplog.set_level(logging.WARNING)

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
            # Intentionally skipping 5, 6
            'seven': 7,
            'eight': 8,
            'nine': 9,
        }
        return names_to_gids[sect_name]


    monkeypatch.setattr(aclient, 'get_section_gids_in_project_or_utl',
            mock_get_section_gids_in_project_or_utl)
    monkeypatch.setattr(aclient, 'get_section_gid_from_name',
            mock_get_section_gid_from_name)

    assert autils.get_net_include_section_gids(0) == {1, 2, 3, 4, 5, 6}

    assert autils.get_net_include_section_gids(0, ['one', 'two']) == {1, 2}

    assert autils.get_net_include_section_gids(0,
            ['one'], [2, 3], ['four']) == {1, 2, 3}

    assert autils.get_net_include_section_gids(0, exclude_sect_gids=[5],
            exclude_sect_names=['three', 'one']) == {2, 4, 6}

    assert autils.get_net_include_section_gids(0,
            exclude_sect_gids=[1, 2], default_to_include=False) == set()

    with pytest.raises(autils.DataMissingError) as ex:
        autils.get_net_include_section_gids(0, [], [7])
    assert 'Section names/gids explicitly included are missing' in str(ex.value)
    assert 'provided by name): 7.' in str(ex.value)
    assert 'Also check names:' not in str(ex.value)

    with pytest.raises(autils.DataMissingError) as ex:
        autils.get_net_include_section_gids(0, ['seven', 'nine'], [7, 8, 10],
                ['eight'])
    assert 'Section names/gids explicitly included are missing' in str(ex.value)
    assert 'provided by name): 8, 9, 10, 7.' in str(ex.value)
    assert 'Also check names: `eight`, `nine`, `seven`.' in str(ex.value)

    caplog.clear()
    assert autils.get_net_include_section_gids(0, ['one'], [2, 3],
            ['seven', 'eight'], [8, 9, 10]) == {1, 2, 3}
    assert caplog.record_tuples == [
            ('asana_extensions.asana.utils', logging.WARNING,
                'Section names/gids explicitly excluded are missing from'
                + ' project/user task list. This may be unintentional.'
                + ' Check gids (some may not be explicitly in list if'
                + ' provided by name): 8, 9, 10, 7. Also check names:'
                + ' `eight`, `seven`.'),
    ]

    caplog.clear()
    with pytest.raises(autils.DataConflictError) as ex:
        autils.get_net_include_section_gids(0, ['one', 'two', 'three'],
                [4, 5, 6], ['one', 'four'], [2, 5, 7])
    assert caplog.record_tuples == [
            ('asana_extensions.asana.utils', logging.WARNING,
                'Section names/gids explicitly excluded are missing from'
                + ' project/user task list. This may be unintentional.'
                + ' Check gids (some may not be explicitly in list if'
                + ' provided by name): 7.'),
    ]
    assert 'Explicit section names/gids cannot be simultaneously' \
            in str(ex.value)
    assert 'provided by name): 1, 2, 4, 5' in str(ex.value)
    assert 'Also check names: `one`, `two`, `four`.' in str(ex.value)

    with pytest.raises(autils.DataConflictError) as ex:
        autils.get_net_include_section_gids(0, ['one', 'two', 'three'],
                [4, 5, 6], ['seven', 'eight'], [4, 5])
    assert 'Explicit section names/gids cannot be simultaneously' \
            in str(ex.value)
    assert 'provided by name): 4, 5' in str(ex.value)
    assert 'Also check names:' not in str(ex.value)
