#!/usr/bin/env python3
"""
Tests the asana_extensions.rules.rules functionality.

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

from asana_extensions.general import dirs
from asana_extensions.rules import rules



logger = logging.getLogger(__name__)



def test_load_all_from_config(monkeypatch, caplog):
    """
    Tests the `test_load_all_from_config()` method.
    """
    def mock_get_conf_path():
        """
        Overrides to point to mock configs dir path so reading config file will
        use this dir instead.
        """
        return os.path.join(os.path.dirname(os.path.realpath(__file__)),
            'test_rules')

    monkeypatch.setattr(dirs, 'get_conf_path', mock_get_conf_path)

    caplog.set_level(logging.WARNING)

    caplog.clear()
    loaded_rules = rules.load_all_from_config('mock_rules.conf')
    assert len(loaded_rules) == 1
    assert caplog.record_tuples == [
            ('asana_extensions.rules.move_tasks_rule', logging.ERROR,
                "Failed to create Move Tasks Rule from config: Must specify to"
                + " use a project or user task list, but not both."),
            ('asana_extensions.rules.rules', logging.WARNING,
                'Matched rule type but failed to parse for rules.conf section'
                + ' "test-move-tasks-no-proj-no-utl"'),
            ('asana_extensions.rules.rules', logging.WARNING,
                'Failed to match any rule type for rules.conf section'
                + ' "test-unknown-rule-type"'),
            ('asana_extensions.rules.rules', logging.WARNING,
                'Failed to match any rule type for rules.conf section'
                + ' "test-no-rule-type"'),
    ]



def test_execute_rules(monkeypatch, caplog, blank_rule_cls):
    """
    Tests the `execute_rules() method.
    """
    def mock_execute(self, force_test_report_only=False):
        """
        Overrides execution to sometimes return failure or add log message.
        """
        if self._rule_type == 'bad-rule-type':
            return False
        if force_test_report_only:
            logger.info(f'Test report only for {self._rule_id}')
        return True

    monkeypatch.setattr(blank_rule_cls, 'execute', mock_execute)

    caplog.set_level(logging.INFO)

    blank_rules = [
        blank_rule_cls('blank-rule-id-1', 'good-rule-type', False),
        blank_rule_cls('blank-rule-id-2', 'good-rule-type', False),
        blank_rule_cls('blank-rule-id-3', 'bad-rule-type', True),
        blank_rule_cls('blank-rule-id-4', 'good-rule-type', False),
    ]

    caplog.clear()
    assert rules.execute_rules(blank_rules) is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.rules', logging.ERROR,
            'Failure in fully executing "blank-rule-id-3".'),
    ]

    caplog.clear()
    assert rules.execute_rules(blank_rules, True) is False
    assert caplog.record_tuples == [
        ('tests.unit.rules.test_rules', logging.INFO,
            'Test report only for blank-rule-id-1'),
        ('tests.unit.rules.test_rules', logging.INFO,
            'Test report only for blank-rule-id-2'),
        ('asana_extensions.rules.rules', logging.ERROR,
            'Failure in fully executing "blank-rule-id-3".'),
        ('tests.unit.rules.test_rules', logging.INFO,
            'Test report only for blank-rule-id-4'),
    ]

    caplog.clear()
    assert rules.execute_rules(blank_rules[3:]) is True
    assert caplog.record_tuples == []

    caplog.clear()
    assert rules.execute_rules(blank_rules[:2], True) is True
    assert caplog.record_tuples == [
        ('tests.unit.rules.test_rules', logging.INFO,
            'Test report only for blank-rule-id-1'),
        ('tests.unit.rules.test_rules', logging.INFO,
            'Test report only for blank-rule-id-2'),
    ]
