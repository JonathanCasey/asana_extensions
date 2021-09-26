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

import os.path

import pytest

from asana_extensions.general import config
from asana_extensions.rules import move_tasks_rule




def test_load_specific_from_config():
    """
    Tests the `load_specific_from_config()` method in `MoveTasksRule`.

    Also effectively tests `__init__()` method in `MoveTasksRule`.  If logic
    added to `__init__()` that goes beyond what is relevant for this
    `load_specific_from_config()` method, then a separate test for init should
    be added.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_move_tasks_rule')
    rules_cp = config.read_conf_file('mock_rules.conf', conf_dir)

    # rule_kwargs = {
    #         'rule_type': move_tasks_rule.MoveTasksRule.get_rule_type_names()[0],
    # }

    with pytest.raises(AssertionError):
        move_tasks_rule.MoveTasksRule.load_specific_from_config(rules_cp,
                'test-full')







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
