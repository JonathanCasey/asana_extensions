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
import logging
import os.path

from asana_extensions.general import dirs
from asana_extensions.rules import rules



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
