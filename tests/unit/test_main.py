#!/usr/bin/env python3
"""
Tests the asana_extensions.main functionality.

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

from asana_extensions import main
from asana_extensions.rules import rules as rules_mod



def test__main_rules(monkeypatch, caplog):
    """
    Tests the `_main_rules()` method.
    """
    def mock_load_all_from_config_success(
                conf_rel_file='rules.conf'):   # pylint: disable=unused-argument
        """
        Return some simple items to use as return "rules".
        """
        return [-1, -2]

    def mock_load_all_from_config_failure(
                conf_rel_file='rules.conf'):   # pylint: disable=unused-argument
        """
        Return some simple items to use as return "rules".
        """
        return [-3, -4]

    def mock_execute_rules(rules, force_test_report_only=False):
        """
        Return True/False, but demonstrate args being used.
        """
        if force_test_report_only:
            rules_mod.logger.info('Test report only')
        if -3 in rules:
            return False
        return True

    monkeypatch.setattr(rules_mod, 'load_all_from_config',
            mock_load_all_from_config_success)
    monkeypatch.setattr(rules_mod, 'execute_rules', mock_execute_rules)

    caplog.set_level(logging.INFO)

    caplog.clear()
    assert main._main_rules(False) is True
    assert caplog.record_tuples == []

    caplog.clear()
    assert main._main_rules(True) is True
    assert caplog.record_tuples == [
        ('asana_extensions.rules.rules', logging.INFO, 'Test report only'),
    ]

    monkeypatch.setattr(rules_mod, 'load_all_from_config',
            mock_load_all_from_config_failure)

    caplog.clear()
    assert main._main_rules(False) is False
    assert caplog.record_tuples == []

    caplog.clear()
    assert main._main_rules(True) is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.rules', logging.INFO, 'Test report only'),
    ]
