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
import uuid

from dateutil.relativedelta import relativedelta
import pytest

from asana_extensions.asana import client as aclient
from asana_extensions.asana import utils as autils
from tests.unit.asana import tester_data



@pytest.fixture(name='tasks_with_due_in_utl_test', scope='session')
def fixture_tasks_with_due_in_utl_test(sections_in_utl_test):
    """
    Creates tasks with and without due dates/times in the user task list (in the
    test workspace), and returns a list of them, each of which is the dict of
    data that should match the `data` element returned by the API.

    Will delete the tasks once done with all tests.

    This is not being used with the autouse keyword so that, if running tests
    that do not require this section fixture, they can run more optimally
    without the need to needlessly create and delete this section.  (Also,
    could not figure out how to get rid of all syntax and pylint errors).

    ** Consumes 20 API calls. **
    (API call count is 2*num_tasks + 2)
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    task_due_params = [
        {'due_on': '2021-01-01'},   # 0
        {'due_on': '2020-12-31'},   # 1
        {'due_on': '2021-01-02'},   # 2
        {'due_at': '2021-01-01T21:00:00-0500'}, # 3
        {'due_at': '2021-01-02T21:00:00-0500'}, # 4
        {'due_at': '2021-01-02T02:00:00Z'},     # 5
        {'due_at': '2021-01-01T21:00:00Z'},     # 6
        {},     # 7
        {'due_on': '2021-01-01', 'completed': True},    # 8
    ]
    client = aclient._get_client()
    me_data = aclient._get_me()
    ws_gid = aclient.get_workspace_gid_from_name(tester_data._WORKSPACE)

    task_data_list = []
    for task_due_param in task_due_params:
        task_name = tester_data._TASK_TEMPLATE.substitute({'tid': uuid.uuid4()})
        params = {
            'assignee': me_data['gid'],
            'assignee_section': sections_in_utl_test[1]['gid'],
            'name': task_name,
            'workspace': str(ws_gid),
        }
        params = {**params, **task_due_param}
        task_data = client.tasks.create_task(params)
        task_data_list.append(task_data)

    yield task_data_list

    for task_data in task_data_list:
        client.tasks.delete_task(task_data['gid'])



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



def test_get_filtered_tasks( # pylint: disable=too-many-locals, too-many-statements
        sections_in_utl_test, tasks_with_due_in_utl_test):
    """
    Tests the `get_filtered_tasks()` method.

    This intentionally falls thru to test `_filter_tasks_by_datetime()` and the
    asana API, as it is critical to detect any functional breakages here.

    These test cases (or at least the data) are largely aligned with
    `test__filter_tasks_by_datetime()`.

    ** Consumes at least 13 API calls. **
    (varies depending on data size, but only 10 calls intended)
    """
    with pytest.raises(AssertionError) as ex:
        autils.get_filtered_tasks(0)
    assert 'Must provide min/max until due or specify no due date but not' \
            + ' both' in str(ex.value)

    with pytest.raises(AssertionError) as ex:
        autils.get_filtered_tasks(0, True, relativedelta())
    assert 'Must provide min/max until due or specify no due date but not' \
            + ' both' in str(ex.value)

    # Use same section gid as used in `tasks_with_due_in_utl_test`
    sect_gid = sections_in_utl_test[1]['gid']
    # Will be comparing task names only
    created_task_gids = [t['gid'] for t in tasks_with_due_in_utl_test]

    filt_tasks = autils.get_filtered_tasks(sect_gid, True)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [7]} \
            == {t['gid'] for t in tasks_to_check}
    assert tasks_to_check[0]['completed'] is False
    assert 'due_at' in tasks_to_check[0]
    assert 'due_on' in tasks_to_check[0]
    assert tasks_to_check[0]['name'] == tasks_with_due_in_utl_test[7]['name']
    assert tasks_to_check[0]['resource_type'] == 'task'

    tzinfo_1 = dt.timezone(dt.timedelta(hours=-5))
    tzinfo_2 = dt.timezone(dt.timedelta(hours=0))

    dt_base_1 = dt.datetime(2021, 1, 1, 21, 0, tzinfo=tzinfo_1)

    rd_date_today = relativedelta(days=0)
    rd_date_tomorrow = relativedelta(days=1)
    rd_date_yesterday = relativedelta(days=-1)
    rd_datetime_2h_later = relativedelta(hours=2)
    rd_datetime_1m_ago = relativedelta(minutes=-1)
    rd_datetime_yesterday_and_1m_ago = relativedelta(days=-1, minutes=-1)

    assumed_time_1 = dt.time(21, 0)
    assumed_time_2 = dt.time(23, 30)

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_date_today,
            rd_date_today, assumed_time_1, use_tzinfo=tzinfo_1,
            dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [0, 3, 5, 6]} \
            == {t['gid'] for t in tasks_to_check}

    # To test if the use_tzinfo default arg is work, need to compensate based
    #  on system timezone and re-call previous test.
    tz_diff = dt_base_1.utcoffset() - dt_base_1.astimezone(None).utcoffset()
    dt_base_1_tz_diffed = dt_base_1 + tz_diff
    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_date_today,
            rd_date_today, dt_base=dt_base_1_tz_diffed)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [0, 3, 5, 6]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_date_today,
            rd_date_today, use_tzinfo=tzinfo_2, dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [2, 4]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_date_today,
            rd_date_today, is_completed=True, use_tzinfo=tzinfo_1,
            dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [8]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_date_today,
            rd_date_today, is_completed=None, use_tzinfo=tzinfo_1,
            dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [0, 3, 5, 6, 8]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_date_today,
            rd_date_tomorrow, None, assumed_time_1, use_tzinfo=tzinfo_1,
            dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [0, 2, 3, 4, 5, 6]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, None,
            rd_date_yesterday, use_tzinfo=tzinfo_1, dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [1]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_date_tomorrow,
            None, use_tzinfo=tzinfo_1, dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [2, 4]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_datetime_1m_ago,
            rd_datetime_2h_later, assumed_time_1, use_tzinfo=tzinfo_1,
            dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [3, 5]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False, rd_datetime_1m_ago,
            rd_datetime_2h_later, assumed_time_1, assumed_time_1,
            use_tzinfo=tzinfo_1, dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [0, 3, 5]} \
            == {t['gid'] for t in tasks_to_check}

    filt_tasks = autils.get_filtered_tasks(sect_gid, False,
            rd_datetime_yesterday_and_1m_ago, rd_datetime_2h_later,
            assumed_time_1, assumed_time_2, use_tzinfo=tzinfo_1,
            dt_base=dt_base_1)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [1, 3, 5, 6]} \
            == {t['gid'] for t in tasks_to_check}

    # Assumes all tasks in the past by more than a few days!
    filt_tasks = autils.get_filtered_tasks(sect_gid, False, None,
            rd_datetime_1m_ago)
    tasks_to_check = [t for t in filt_tasks if t['gid'] in created_task_gids]
    assert {created_task_gids[i] for i in [3, 4, 5, 6]} \
            == {t['gid'] for t in tasks_to_check}



def test__filter_tasks_by_datetime():      # pylint: disable=too-many-statements
    """
    Tests the `_filter_tasks_by_datetime()` method.

    These test cases (or at least the data) are largely aligned with
    `test_get_filtered_tasks()`.
    """
    # 'due_on' corresponds to 'due_at' as though set in UTC-0500 timezone
    all_tasks = [
        {'t': 0, 'due_on': '2021-01-01'},
        {'t': 1, 'due_on': '2020-12-31'},
        {'t': 2, 'due_on': '2021-01-02', 'due_at': None},
        {'t': 3, 'due_at': '2021-01-01T21:00-0500', 'due_on': '2021-01-01'},
        {'t': 4, 'due_at': '2021-01-02T21:00-0500', 'due_on': '2021-01-02'},
        {'t': 5, 'due_at': '2021-01-02T02:00Z', 'due_on': '2021-01-01'},
        {'t': 6, 'due_at': '2021-01-01T21:00Z', 'due_on': '2021-01-01'},
        {'t': 7, 'due_on': None, 'due_at': None},
        {'t': 8, 'due_at': '2021-01-02 21:00', 'due_on': 'bad timezone'},
        {'t': 9, 'no_due_key': 'this is bad'},
    ]
    good_tasks = all_tasks[:8]

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
    assert filt_tasks == good_tasks[:7]

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
    assert filt_tasks == good_tasks[:7]

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
        autils._filter_tasks_by_datetime(all_tasks[8:], dt_base_1,
                rd_datetime_2h_later, operator.ge)
    assert "can't compare offset-naive and offset-aware datetimes" \
            in str(ex.value)
    with pytest.raises(KeyError) as ex:
        autils._filter_tasks_by_datetime(all_tasks[9:], dt_base_1,
                rd_date_today, operator.ge)
    assert 'due_on' in str(ex.value)



def test__filter_tasks_by_completed():
    """
    Tests the `_filter_tasks_by_completed()` method.
    """
    all_tasks = [
        {'t': 0, 'completed': True},
        {'t': 1, 'completed': False},
        {'t': 2, 'completed': False},
        {'t': 3, 'completed': True},
        {'t': 4, 'no_completed': 'this is bad'},
    ]
    good_tasks = all_tasks[:4]

    filt_tasks = autils._filter_tasks_by_completed(good_tasks, None)
    assert filt_tasks == good_tasks

    filt_tasks = autils._filter_tasks_by_completed(good_tasks, True)
    assert filt_tasks == [all_tasks[i] for i in [0, 3]]

    filt_tasks = autils._filter_tasks_by_completed(good_tasks, False)
    assert filt_tasks == [all_tasks[i] for i in [1, 2]]

    with pytest.raises(KeyError) as ex:
        autils._filter_tasks_by_completed(all_tasks, True)
    assert 'completed' in str(ex.value)
