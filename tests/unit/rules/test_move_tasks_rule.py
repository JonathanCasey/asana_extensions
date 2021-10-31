#!/usr/bin/env python3
"""
Tests the asana_extensions.rules.move_tasks_rule functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import copy
import logging
import os.path

import asana
import pytest

from asana_extensions.asana import client as aclient
from asana_extensions.asana import utils as autils
from asana_extensions.general import config
from asana_extensions.rules import move_tasks_rule
from asana_extensions.rules import rule_meta
from tests.unit.rules import test_rule_meta



@pytest.fixture(name='blank_move_tasks_rule')
def fixture_blank_move_tasks_rule():
    """
    Returns a blank move tasks rule that does the absolute bare minimum to be
    initialized (though may add some extra if it helps cover more tests easily).

    Tests using this could always "hack" in more _rule_params if the test knows
    what it is doing.
    """
    kwargs = {
        'rule_id': 'blank rule id',
        'rule_type': 'move tasks',
        'test_report_only': True,
    }
    # At very least, need to define all keys in `__init__()` and pass asserts
    rule_params = {
        'project_name': None,
        'project_gid': -1,
        'is_my_tasks_list': None,
        'user_task_list_gid': None,
        'workspace_name': None,
        'workspace_gid': -2,
        'min_time_until_due_str': None,
        'max_time_until_due_str': None,
        'min_time_until_due': None,
        'max_time_until_due': None,
        'match_no_due_date': True,
        # Below added for `_sync_and_validate_with_api()`
        'src_sections_include_names': None,
        'src_sections_include_gids': None,
        'src_sections_exclude_names': None,
        'src_sections_exclude_gids': None,
        'dst_section_name': None,
        'dst_section_gid': -3,
    }
    return move_tasks_rule.MoveTasksRule(rule_params, **kwargs)



def test_load_specific_from_conf(caplog):  # pylint: disable=too-many-statements
    """
    Tests the `load_specific_from_conf()` method in `MoveTasksRule`.

    Also effectively tests `__init__()` method in `MoveTasksRule`.  If logic
    added to `__init__()` that goes beyond what is relevant for this
    `load_specific_from_conf()` method, then a separate test for init should
    be added.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_move_tasks_rule')
    rules_cp = config.read_conf_file('mock_move_tasks_rules.conf', conf_dir)

    caplog.set_level(logging.WARNING)

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-success')
    assert rule is not None
    assert caplog.record_tuples == []

    with pytest.raises(AssertionError) as ex:
        move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-full', {'dummy key': 'dummy val'})
    assert "Should not pass anything in for `rule_params`" in str(ex.value)

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-essential-missing-key')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.rule_meta', logging.ERROR,
                "Failed to parse Rule from config.  Check keys.  Exception:"
                + " 'rule type'"),
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to parse Move Tasks Rule from config.  Check keys."
                + "  Exception: 'rule type'"),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-full')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:" \
                    " Cannot specify 'for my tasks list' and" \
                    + " 'user task list gid' together."),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-invalid-boolean')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to parse Move Tasks Rule from config.  Check strong"
                + " typed values.  Exception: Not a boolean: 42"),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-is-utl-and-gid')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:" \
                    " Cannot specify 'for my tasks list' and" \
                    + " 'user task list gid' together."),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-no-proj-no-utl')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify to use a project or user task list, but not"
                + " both."),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-both-proj-and-utl')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify to use a project or user task list, but not"
                + " both."),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-no-workspace')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify workspace."),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
                'test-move-tasks-timeframe-parse-fail')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to parse Move Tasks Rule from config.  Check timeframe"
                + " args.  Exception: Could not parse time frame - Found 2"
                + " entries for minutes?/m when only 0-1 allowed."),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
                'test-move-tasks-time-parse-fail')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to parse Move Tasks Rule from config.  Check time args."
                + "  Exception: Timezone prohibited for time string, but one was"
                + " provided.  String: '12:23:45+00:00', parsed:"
                + " `12:23:45+00:00`"),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-both-time-until-and-no-due')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify either min/max time until due or match no" \
                + " due date (but not both)."),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-time-neither-time-until-nor-no-due')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify either min/max time until due or match no" \
                + " due date (but not both)."),
    ]



def test_load_specific_from_conf__impossible(monkeypatch, caplog):
    """
    Tests "impossible" cases in the `load_specific_from_conf()` method in
    `MoveTasksRule`.  These require mocking, as normally these are not possible
    due to logic in submethods called.  This ensures that even if that logic
    were to change in the future, this `load_specific_from_conf()` would still
    handle the situation.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_move_tasks_rule')
    rules_cp = config.read_conf_file('mock_move_tasks_rules.conf', conf_dir)

    caplog.set_level(logging.WARNING)

    def mock_parse_timedelta_arg_pass(arg_str): # pylint: disable=unused-argument
        """
        Forces timedelta parser to return something.
        """
        return ''

    monkeypatch.setattr(rule_meta.Rule, 'parse_timedelta_arg',
            mock_parse_timedelta_arg_pass)

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-time-neither-time-until-nor-no-due')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Failed to parse min/max time until due -- check format."),
    ]


    def mock_parse_timedelta_arg_fail(arg_str): # pylint: disable=unused-argument
        """
        Forces timedelta parser to return as if nothing parsed.
        """
        return None

    monkeypatch.setattr(rule_meta.Rule, 'parse_timedelta_arg',
            mock_parse_timedelta_arg_fail)

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-time-parse-fake-fail')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Failed to parse min/max time until due -- check format."),
    ]



def test_get_rule_type_names():
    """
    Tests the `get_rule_type_names()` method in `MoveTasksRule`.  Not an
    exhaustive test.
    """
    assert 'move tasks' in move_tasks_rule.MoveTasksRule.get_rule_type_names()
    assert 'auto-promote tasks' \
            in move_tasks_rule.MoveTasksRule.get_rule_type_names()
    assert 'auto-promote' in move_tasks_rule.MoveTasksRule.get_rule_type_names()
    assert 'auto promote tasks' \
            in move_tasks_rule.MoveTasksRule.get_rule_type_names()
    assert 'auto promote' in move_tasks_rule.MoveTasksRule.get_rule_type_names()
    assert 'promote tasks' \
            in move_tasks_rule.MoveTasksRule.get_rule_type_names()
    assert 'not move tasks' \
            not in move_tasks_rule.MoveTasksRule.get_rule_type_names()



def test__sync_and_validate_with_api(      # pylint: disable=too-many-statements
        monkeypatch, caplog, blank_move_tasks_rule):
    """
    Tests the `_sync_and_validate_with_api()` method in `MoveTasksRule`.

    The general design is to have mock functions that can return values to allow
    the code to continue; but can pass in an alternative value to trigger an
    exception.  Between all of the mock functions, all possible exceptions
    caught by `_sync_and_validate_with_api()` are tested.
    """
    def mock_get_workspace_gid_from_name(ws_name, ws_gid=None):
        """
        Return the matching gid (if not triggering exception).
        """
        # pylint: disable=unused-argument
        if ws_name == 'raise-client-creation-error':
            raise aclient.ClientCreationError(ws_name)
        return -102

    def mock_get_user_task_list_gid(workspace_gid, is_me=False, user_gid=None):
        """
        Return the matching gid (if not triggering exception).
        """
        # pylint: disable=unused-argument
        if workspace_gid == 'raise-asana-error':
            raise asana.error.InvalidRequestError(workspace_gid)
        return -104

    def mock_get_project_gid_from_name(ws_gid, proj_name, proj_gid=None,
            archived=False):
        """
        Return the matching gid (if not triggering exception).
        """
        # pylint: disable=unused-argument
        if ws_gid == 'raise-data-not-found-error':
            raise aclient.DataNotFoundError(ws_gid)
        return -101

    def mock_get_net_include_section_gids(proj_or_utl_gid,
            include_sect_names=None, include_sect_gids=None,
            exclude_sect_names=None, exclude_sect_gids=None,
            default_to_include=True):
        """
        Return some gids (if not triggering exception).
        """
        # pylint: disable=unused-argument
        if proj_or_utl_gid == 'raise-data-conflict-error':
            raise autils.DataConflictError(proj_or_utl_gid)
        if proj_or_utl_gid == 'raise-data-missing-error':
            raise autils.DataMissingError(proj_or_utl_gid)
        return [-105, -106]

    def mock_get_section_gid_from_name(proj_or_utl_gid, sect_name,
            sect_gid=None):
        """
        Return the matching gid (if not triggering exception).
        """
        # pylint: disable=unused-argument
        if proj_or_utl_gid == 'raise-duplicate-name-error':
            raise aclient.DuplicateNameError(proj_or_utl_gid)
        if proj_or_utl_gid == 'raise-mismatched-data-error':
            raise aclient.MismatchedDataError(proj_or_utl_gid)
        return -103

    monkeypatch.setattr(aclient, 'get_workspace_gid_from_name',
            mock_get_workspace_gid_from_name)
    monkeypatch.setattr(aclient, 'get_user_task_list_gid',
            mock_get_user_task_list_gid)
    monkeypatch.setattr(aclient, 'get_project_gid_from_name',
            mock_get_project_gid_from_name)
    monkeypatch.setattr(autils, 'get_net_include_section_gids',
            mock_get_net_include_section_gids)
    monkeypatch.setattr(aclient, 'get_section_gid_from_name',
            mock_get_section_gid_from_name)

    bmtr = blank_move_tasks_rule # Shorten name since used so much here

    # All items are int/str/bool, so no need for deep copy
    rule_params_backup = copy.copy(bmtr._rule_params)

    def reset_rule_params():
        """
        Restore the rule params for the blank rule to the original/backup.
        """
        bmtr._rule_params = copy.copy(rule_params_backup)

    caplog.set_level(logging.ERROR)

    assert bmtr._sync_and_validate_with_api() is True
    assert bmtr._rule_params['workspace_gid'] == -2
    assert bmtr._rule_params['project_gid'] == -1
    assert bmtr._rule_params['user_task_list_gid'] is None
    assert bmtr._rule_params['effective_project_gid'] == -1
    assert bmtr._rule_params['src_net_include_section_gids'] == [-105, -106]
    assert bmtr._rule_params['dst_section_gid'] == -3

    reset_rule_params()
    bmtr._rule_params['workspace_name'] = 'test-ws'
    bmtr._rule_params['project_name'] = 'test-proj'
    bmtr._rule_params['dst_section_name'] = 'test-dst-sect'
    assert bmtr._sync_and_validate_with_api() is True
    assert bmtr._rule_params['workspace_gid'] == -102
    assert bmtr._rule_params['project_gid'] == -101
    assert bmtr._rule_params['user_task_list_gid'] is None
    assert bmtr._rule_params['effective_project_gid'] == -101
    assert bmtr._rule_params['src_net_include_section_gids'] == [-105, -106]
    assert bmtr._rule_params['dst_section_gid'] == -103

    reset_rule_params()
    bmtr._rule_params['project_gid'] = None
    bmtr._rule_params['is_my_tasks_list'] = True
    assert bmtr._sync_and_validate_with_api() is True
    assert bmtr._rule_params['workspace_gid'] == -2
    assert bmtr._rule_params['project_gid'] is None
    assert bmtr._rule_params['user_task_list_gid'] == -104
    assert bmtr._rule_params['effective_project_gid'] == -104
    assert bmtr._rule_params['src_net_include_section_gids'] == [-105, -106]
    assert bmtr._rule_params['dst_section_gid'] == -3

    reset_rule_params()
    bmtr._rule_params['project_gid'] = None
    bmtr._rule_params['user_task_list_gid'] = -4
    assert bmtr._sync_and_validate_with_api() is True
    assert bmtr._rule_params['workspace_gid'] == -2
    assert bmtr._rule_params['project_gid'] is None
    assert bmtr._rule_params['user_task_list_gid'] == -4
    assert bmtr._rule_params['effective_project_gid'] == -4
    assert bmtr._rule_params['src_net_include_section_gids'] == [-105, -106]
    assert bmtr._rule_params['dst_section_gid'] == -3

    msg_base_err  = 'Failed to sync and validate rule "blank rule id" with the'
    msg_base_err += ' API.  Skipping rule.  Exception:'

    caplog.clear()
    reset_rule_params()
    error = 'raise-client-creation-error'
    bmtr._rule_params['workspace_name'] = error
    assert bmtr._sync_and_validate_with_api() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
            f'{msg_base_err} {error}'),
    ]

    caplog.clear()
    reset_rule_params()
    error = 'raise-asana-error'
    bmtr._rule_params['workspace_gid'] = error
    bmtr._rule_params['project_gid'] = None
    bmtr._rule_params['is_my_tasks_list'] = True
    assert bmtr._sync_and_validate_with_api() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
            f'{msg_base_err} Invalid Request'),
    ]

    caplog.clear()
    reset_rule_params()
    error = 'raise-data-not-found-error'
    bmtr._rule_params['workspace_gid'] = error
    bmtr._rule_params['project_name'] = 'test-proj'
    assert bmtr._sync_and_validate_with_api() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
            f'{msg_base_err} {error}'),
    ]

    caplog.clear()
    reset_rule_params()
    error = 'raise-data-conflict-error'
    bmtr._rule_params['project_gid'] = error
    assert bmtr._sync_and_validate_with_api() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
            f'{msg_base_err} {error}'),
    ]

    caplog.clear()
    reset_rule_params()
    error = 'raise-data-missing-error'
    bmtr._rule_params['project_gid'] = error
    assert bmtr._sync_and_validate_with_api() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
            f'{msg_base_err} {error}'),
    ]

    caplog.clear()
    reset_rule_params()
    error = 'raise-duplicate-name-error'
    bmtr._rule_params['project_gid'] = error
    bmtr._rule_params['dst_section_name'] = 'test-dst-sect'
    assert bmtr._sync_and_validate_with_api() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
            f'{msg_base_err} {error}'),
    ]

    caplog.clear()
    reset_rule_params()
    error = 'raise-mismatched-data-error'
    bmtr._rule_params['project_gid'] = error
    bmtr._rule_params['dst_section_name'] = 'test-dst-sect'
    assert bmtr._sync_and_validate_with_api() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
            f'{msg_base_err} {error}'),
    ]



def test_is_valid(monkeypatch, blank_move_tasks_rule):
    """
    Tests the `is_valid()` method in `MoveTasksRule`.

    This is inherited from `Rule` and not overridden, but since it is expected
    that it could be overridden, should be tested.
    """
    def mock__sync_and_validate_with_api():
        """
        Force to return True.
        """
        return True

    monkeypatch.setattr(blank_move_tasks_rule, '_sync_and_validate_with_api',
            mock__sync_and_validate_with_api)
    test_rule_meta.subtest_is_valid(monkeypatch, blank_move_tasks_rule)



def test_is_criteria_met(blank_move_tasks_rule):
    """
    Tests the `is_criteria_met()` method in `MoveTasksRule`.

    This is inherited from `Rule` and not overridden, but since it is expected
    that it could be overridden, should be tested.
    """
    test_rule_meta.subtest_is_criteria_met(blank_move_tasks_rule)



def test_execute(monkeypatch, caplog, blank_move_tasks_rule):
    """
    Tests the `execute()` method in `MoveTasksRule`.
    """
    caplog.set_level(logging.INFO)
    bmtr = blank_move_tasks_rule # Shorten name since used so much here

    def mock_is_valid(self):
        """
        """
        if 'mock_fail_is_valid' in self._rule_params:
            return False
        return True

    def mock_is_criteria_met(self):
        """
        """
        if 'mock_fail_is_criteria_met' in self._rule_params:
            return False
        return True

    monkeypatch.setattr(move_tasks_rule.MoveTasksRule, 'is_valid',
            mock_is_valid)
    monkeypatch.setattr(move_tasks_rule.MoveTasksRule, 'is_criteria_met',
            mock_is_criteria_met)

    # All items are int/str/bool, so no need for deep copy
    rule_params_backup = copy.copy(bmtr._rule_params)

    def reset_rule_params():
        """
        Restore the rule params for the blank rule to the original/backup.
        """
        bmtr._rule_params = copy.copy(rule_params_backup)

    caplog.clear()
    bmtr._rule_params['mock_fail_is_valid'] = True
    assert bmtr.execute() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
            'Failed to execute "blank rule id" since invalid.'),
    ]

    caplog.clear()
    reset_rule_params()
    bmtr._rule_params['mock_fail_is_criteria_met'] = True
    assert bmtr.execute() is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.move_tasks_rule', logging.INFO,
            'Skipping execution of "blank rule id" completely since criteria'
            + ' not met.'),
    ]
