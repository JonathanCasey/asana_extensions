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

import pytest

from asana_extensions import main
from asana_extensions.rules import rules as rules_mod



def test_global():
    """
    Tests items at the global scope not otherwise fully tested.
    """
    # Since only used (right now0 for logger name which is untested code, this
    #  gives the best chance of detecting a mistake there.
    assert main._NAME_MOD_OVERRIDE == 'asana_extensions.main'



def test_main(monkeypatch, caplog):
    """
    Tests the `main()` method.
    """
    def mock__main_rules(force_test_report_only=False):
        """
        Return true/false, but do so based on test report arg for convenience.
        """
        return force_test_report_only

    monkeypatch.setattr(main, '_main_rules', mock__main_rules)

    caplog.set_level(logging.INFO)

    caplog.clear()
    main.main(False, logging.WARNING, [])
    assert caplog.record_tuples == []

    caplog.clear()
    main.main(False, logging.INFO, [])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.INFO,
            'Asana Extensions had no modules to run -- fully skipped.'),
    ]

    caplog.clear()
    main.main(False, logging.INFO, ['rules'])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.WARNING,
            'Asana Extensions run completed, but with errors...'),
    ]

    caplog.clear()
    main.main(True, logging.INFO, ['all'])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.INFO,
            'Asana Extensions run completed successfully!'),
    ]

    caplog.clear()
    main.main(False, 'bad log level', [])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.WARNING,
            "Logger setting failed (Exception: Unknown level: 'BAD LOG LEVEL')."
                + "  Defaulting to not set."),
        ('asana_extensions.main', logging.INFO,
            'Asana Extensions had no modules to run -- fully skipped.'),
    ]



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



def test__config_root_logger():
    """
    Tests the `_config_root_logger()` method.
    """
    root_logger = logging.getLogger()
    assert root_logger.getEffectiveLevel() == logging.WARNING

    main._config_root_logger('info')
    assert root_logger.getEffectiveLevel() == logging.INFO

    main._config_root_logger(15)
    assert root_logger.getEffectiveLevel() == 15

    main._config_root_logger(10)
    assert root_logger.getEffectiveLevel() == logging.DEBUG

    with pytest.raises(ValueError) as ex:
        main._config_root_logger('20')
    assert "Unknown level: '20'" in str(ex.value)

    with pytest.raises(ValueError) as ex:
        main._config_root_logger('invalid-level')
    assert "Unknown level: 'INVALID-LEVEL'" in str(ex.value)

    class Dummy:                        # pylint: disable=too-few-public-methods
        """
        Dummy class that does nothing.
        """

    with pytest.raises(TypeError) as ex:
        main._config_root_logger(Dummy())
    assert 'Invalid log level type (somehow).  See --help for -l.' \
            in str(ex.value)
