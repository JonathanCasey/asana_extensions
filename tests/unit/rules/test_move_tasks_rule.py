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

import logging
import os.path

import pytest

from asana_extensions.general import config
from asana_extensions.rules import move_tasks_rule
from asana_extensions.rules import rule_meta



def test_load_specific_from_conf(caplog):
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
            'test-invalid-boolean')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to parse Move Tasks Rule from config.  Check strong"
                + " typed values.  Exception: Not a boolean: 42")
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-full-is-utl-and-gid')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:" \
                    " Cannot specify 'is my tasks list' and" \
                    + " 'user task list gid' together.")
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-no-proj-no-utl')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify to use a project or user task list, but not"
                + " both.")
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-both-proj-and-utl')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify to use a project or user task list, but not"
                + " both.")
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-no-workspace')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify workspace.")
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
                'test-move-tasks-time-parse-fail')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to parse Move Tasks Rule from config.  Check time args."
                + "  Exception: Could not parse time frame - Found 2 entries"
                + " for minutes?/m when only 0-1 allowed."),
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-both-time-until-and-no-due')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify either min/max time until due or match no" \
                + " due date (but not both).")
    ]

    caplog.clear()
    rule = move_tasks_rule.MoveTasksRule.load_specific_from_conf(rules_cp,
            'test-move-tasks-time-neither-time-until-nor-no-due')
    assert rule is None
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config:"
                + " Must specify either min/max time until due or match no" \
                + " due date (but not both).")
    ]



def test_load_specific_from_conf_impossible(monkeypatch, caplog):
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
                + " Failed to parse min/max time until due -- check format.")
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
                + " Failed to parse min/max time until due -- check format.")
    ]



def test_get_provider_names():
    """
    Tests the `get_provider_names()` method in `MoveTasksRule`.  Not an
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
