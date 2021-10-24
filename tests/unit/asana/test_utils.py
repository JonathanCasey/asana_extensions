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
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import datetime as dt
import logging
import operator

from dateutil.relativedelta import relativedelta
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



def test__filter_tasks_by_datetime():      # pylint: disable=too-many-statements
    """
    Tests the `_filter_tasks_by_datetime()` method.
    """
    # 'due_on' corresponds to 'due_at' as though set in UTC-0500 timezone
    all_tasks = [
        {'t': 0, 'due_on': '2021-01-01'},
        {'t': 1, 'due_on': '2020-12-31'},
        {'t': 2, 'due_on': '2021-01-02'},
        {'t': 3, 'due_at': '2021-01-01T21:00-0500', 'due_on': '2021-01-01'},
        {'t': 4, 'due_at': '2021-01-02T21:00-0500', 'due_on': '2021-01-02'},
        {'t': 5, 'due_at': '2021-01-02T02:00Z', 'due_on': '2021-01-01'},
        {'t': 6, 'due_at': '2021-01-01T21:00Z', 'due_on': '2021-01-01'},
        {'t': 7, 'due_at': '2021-01-02 21:00', 'due_on': 'bad timezone'},
        {'t': 8, 'no_due_key': 'this is bad'},
    ]
    good_tasks = all_tasks[:7]

    dt_base_1 = dt.datetime(2021, 1, 1, 21, 0, tzinfo=dt.timezone(
            dt.timedelta(hours=-5)))
    dt_base_2 = dt.datetime(2021, 1, 1, 19, 0, tzinfo=dt.timezone(
            dt.timedelta(hours=-5)))
    dt_base_3 = dt.datetime(2021, 1, 2, 0, 0, tzinfo=dt.timezone(
            dt.timedelta(hours=0))) # Same as dt_base_2, but different timezone
    dt_base_4 = dt.datetime(2021, 1, 2, 2, 0, tzinfo=dt.timezone(
            dt.timedelta(hours=0))) # Same as dt_base_1, but different timezone

    rd_date_today = relativedelta(days=0)
    rd_datetime_2h_later = relativedelta(hours=2)

    assumed_time_1 = dt.time(21, 0)
    assumed_time_2 = dt.time(23, 0)
    assumed_time_3 = dt.time(1, 0)

    # Set 1: No filter
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1, None,
            operator.lt)
    assert filt_tasks == good_tasks

    # Set 2: Date filter
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_date_today, operator.ge)
    assert filt_tasks == [all_tasks[i] for i in [0, 2, 3, 4, 5, 6]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_date_today, operator.le)
    assert filt_tasks == [all_tasks[i] for i in [0, 1, 3, 5, 6]]

    # Set 3: Datetime filter
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_datetime_2h_later, operator.ge)
    assert filt_tasks == [all_tasks[i] for i in [4]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_datetime_2h_later, operator.lt)
    assert filt_tasks == [all_tasks[i] for i in [3, 5, 6]]

    # Set 4: Datetime filter, different time but same tz as Set 3
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_2,
            rd_datetime_2h_later, operator.ge)
    assert filt_tasks == [all_tasks[i] for i in [3, 4, 5]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_2,
            rd_datetime_2h_later, operator.lt)
    assert filt_tasks == [all_tasks[i] for i in [6]]

    # Set 5: Date filter, different tz than Set 2
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_3,
            rd_date_today, operator.ge)
    assert filt_tasks == [all_tasks[i] for i in [2, 4]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_3,
            rd_date_today, operator.le)
    assert filt_tasks == good_tasks

    # Set 6: Datetime filter, different tz than Set 4 (no effect)
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_3,
            rd_datetime_2h_later, operator.ge)
    assert filt_tasks == [all_tasks[i] for i in [3, 4, 5]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_3,
            rd_datetime_2h_later, operator.lt)
    assert filt_tasks == [all_tasks[i] for i in [6]]

    # Set 7: Date filter, assumed time added to Set 5 (no effect)
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_3,
            rd_date_today, operator.ge, assumed_time_1)
    assert filt_tasks == [all_tasks[i] for i in [2, 4]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_3,
            rd_date_today, operator.le, assumed_time_1)
    assert filt_tasks == good_tasks

    # Set 8: Datetime filter, assumed time added to Set 3
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_datetime_2h_later, operator.ge, assumed_time_1)
    assert filt_tasks == [all_tasks[i] for i in [2, 4]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_datetime_2h_later, operator.lt, assumed_time_1)
    assert filt_tasks == [all_tasks[i] for i in [0, 1, 3, 5, 6]]

    # Set 9: Datetime filter, different assumed time than Set 8
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_datetime_2h_later, operator.ge, assumed_time_2)
    assert filt_tasks == [all_tasks[i] for i in [0, 2, 4]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_datetime_2h_later, operator.lt, assumed_time_2)
    assert filt_tasks == [all_tasks[i] for i in [1, 3, 5, 6]]

    # Set 10: Datetime filter, different assumed time than Set 8
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_datetime_2h_later, operator.ge, assumed_time_3)
    assert filt_tasks == [all_tasks[i] for i in [2, 4]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_1,
            rd_datetime_2h_later, operator.lt, assumed_time_3)
    assert filt_tasks == [all_tasks[i] for i in [0, 1, 3, 5, 6]]

    # Set 11: Datetime filter, different timezone than Set 10
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_4,
            rd_datetime_2h_later, operator.ge, assumed_time_3)
    assert filt_tasks == [all_tasks[i] for i in [4]]
    filt_tasks = autils._filter_tasks_by_datetime(good_tasks, dt_base_4,
            rd_datetime_2h_later, operator.lt, assumed_time_3)
    assert filt_tasks == [all_tasks[i] for i in [0, 1, 2, 3, 5, 6]]

    # Set 12: Failure modes
    with pytest.raises(TypeError) as ex:
        autils._filter_tasks_by_datetime(all_tasks[7:], dt_base_1,
                rd_datetime_2h_later, operator.ge)
    assert "can't compare offset-naive and offset-aware datetimes" \
            in str(ex.value)
    with pytest.raises(KeyError) as ex:
        autils._filter_tasks_by_datetime(all_tasks[8:], dt_base_1,
                rd_date_today, operator.ge)
    assert 'due_on' in str(ex.value)
