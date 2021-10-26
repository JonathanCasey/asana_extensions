#!/usr/bin/env python3
"""
Tests the asana_extensions.rules.rule_meta functionality.

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
import os.path

from dateutil.relativedelta import relativedelta
import pytest

from asana_extensions.general import config
from asana_extensions.general.exceptions import *   # pylint: disable=wildcard-import
from asana_extensions.rules import rule_meta



def test_init(caplog):
    """
    Tests `__init__()` method in `Rule`.
    """

    class BlankRule(rule_meta.Rule):
        """
        Simple blank rule to subclass Rule.
        """
        @classmethod
        def load_specific_from_conf(cls, rules_cp, rule_id, rule_params=None,
                **kwargs):
            """
            Not needed / will not be used.
            """
            return

        @classmethod
        def get_rule_type_names(cls):
            """
            Not needed / will not be used.
            """
            return []

    caplog.set_level(logging.WARNING)
    caplog.clear()

    blank_rule = BlankRule('blank-rule-id', 'blank-rule-type', True)
    assert blank_rule._rule_id == 'blank-rule-id'
    assert blank_rule._rule_type == 'blank-rule-type'
    assert blank_rule._test_report_only is True
    assert caplog.record_tuples == []

    blank_extra_rule = BlankRule('blank-rule-id', 'blank-rule-type', True,
            extras='extra-kwarg')
    assert blank_extra_rule._rule_id == 'blank-rule-id'
    assert blank_extra_rule._rule_type == 'blank-rule-type'
    assert blank_extra_rule._test_report_only is True
    assert caplog.record_tuples == [
            ('asana_extensions.rules.rule_meta', logging.WARNING,
                'Discarded excess kwargs provided to BlankRule: extras'),
    ]



def test_load_specific_from_conf(caplog):
    """
    Tests the `load_specific_from_conf()` method in `Rule`.
    """
    class BlankRule(rule_meta.Rule):
        """
        Simple blank rule to subclass Rule.
        """
        def __init__(self, rule_params, **kwargs):
            """
            Only needs to call super and save `rule_params`.
            """
            super().__init__(**kwargs)
            self._rule_params = rule_params

        @classmethod
        def load_specific_from_conf(cls, rules_cp, rule_id, rule_params=None,
                **kwargs):
            """
            Only used to call super-under-test's method-under-test.
            """
            super().load_specific_from_conf(rules_cp, rule_id, rule_params,
                    **kwargs)
            # Want to re-use rule_params to expand keywords for init,
            #  but also allow explicit tests that rule_params loaded properly
            return cls(rule_params, **kwargs, **rule_params, rule_id=rule_id)

        @classmethod
        def get_rule_type_names(cls):
            """
            Not needed / will not be used.
            """
            return []

    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_rule_meta')
    rules_cp = config.read_conf_file('mock_rule_meta.conf', conf_dir)

    caplog.set_level(logging.WARNING)

    with pytest.raises(AssertionError) as ex:
        BlankRule.load_specific_from_conf(rules_cp,
                'test-essential-missing-key')
    assert  "Subclass must provide `rule_params`." in str(ex.value)

    caplog.clear()
    with pytest.raises(KeyError):
        BlankRule.load_specific_from_conf(rules_cp,
                'test-essential-missing-key', {})
    assert caplog.record_tuples == [
            ('asana_extensions.rules.rule_meta', logging.ERROR,
                "Failed to parse Rule from config.  Check keys.  Exception:"
                + " 'rule type'"),
    ]

    caplog.clear()
    with pytest.raises(ValueError):
        BlankRule.load_specific_from_conf(rules_cp,
                'test-invalid-boolean', {})
    assert caplog.record_tuples == [
            ('asana_extensions.rules.rule_meta', logging.ERROR,
                "Failed to parse Rule from config.  Check strong typed values."
                    + "  Exception: Not a boolean: 42"),
    ]

    caplog.clear()
    rule = BlankRule.load_specific_from_conf(rules_cp,
            'test-blank-success', {})
    assert rule is not None
    assert rule._rule_params['rule_type'] == 'blank rule'
    assert caplog.record_tuples == []



def test_parse_time_arg():
    """
    Tests the `parse_time_arg()` method in `Rule`.
    """
    test_str = '13:00'
    test_time = dt.time.fromisoformat(test_str)
    assert rule_meta.Rule.parse_time_arg(test_str) == test_time
    assert rule_meta.Rule.parse_time_arg(test_str, None) == test_time
    with pytest.raises(config.UnsupportedFormatError) as ex:
        rule_meta.Rule.parse_time_arg(test_str, True)
    assert 'Timezone required' in str(ex.value)

    test_str = '13:00-05:00'
    test_time = dt.time.fromisoformat(test_str)
    assert rule_meta.Rule.parse_time_arg(test_str) == test_time
    assert rule_meta.Rule.parse_time_arg(test_str, True) == test_time
    with pytest.raises(config.UnsupportedFormatError) as ex:
        rule_meta.Rule.parse_time_arg(test_str, None)
    assert 'Timezone prohibited' in str(ex.value)

    assert rule_meta.Rule.parse_time_arg(None) is None
    assert rule_meta.Rule.parse_time_arg('', True) is None

    with pytest.raises(AssertionError) as ex:
        rule_meta.Rule.parse_time_arg('', 'invalid value')
    assert '`is_tz_required` must be bool or None' in str(ex.value)

    with pytest.raises(ValueError) as ex:
        rule_meta.Rule.parse_time_arg('bad time str')
    assert 'Invalid isoformat string' in str(ex.value)



def test_parse_timedelta_arg():
    """
    Tests the `parse_timedelta_arg()` method in `Rule`.
    """
    test_str = '1m2h3d4w5M6y'   # How long it takes me to finish a "quick" proj
    assert rule_meta.Rule.parse_timedelta_arg(test_str) == relativedelta(
            minutes=1, hours=2, days=3, weeks=4, months=5, years=6)

    test_str = '1 minutes, 2 hour 3 days4weeks-5MonTHs +6Years'
    assert rule_meta.Rule.parse_timedelta_arg(test_str) == relativedelta(
            minutes=1, hours=2, days=3, weeks=4, months=-5, years=6)

    test_str = ''
    assert rule_meta.Rule.parse_timedelta_arg(test_str) is None

    test_str = '0d'
    assert rule_meta.Rule.parse_timedelta_arg(test_str) == relativedelta()

    test_str = '1h 2hours'
    with pytest.raises(TimeframeArgDupeError):
        rule_meta.Rule.parse_timedelta_arg(test_str)

    assert rule_meta.Rule.parse_timedelta_arg(None) is None



def test_parse_timeframe():
    """
    Tests the `parse_timeframe()` method in `Rule`.
    """
    tf_minutes = {'minutes?': False, 'm': True}
    tf_hours = {'hours?': False, 'h': True}
    tf_days = {'days?': False, 'd': True}
    tf_weeks = {'weeks?': False, 'w': True}
    tf_months = {'months?': False, 'M': True}
    tf_years = {'years?': False, 'y': True}

    test_str = '3m'
    assert rule_meta.Rule.parse_timeframe(test_str, tf_minutes) == 3
    assert rule_meta.Rule.parse_timeframe(test_str, tf_hours) == 0

    test_str = '3m 2m'
    with pytest.raises(TimeframeArgDupeError):
        rule_meta.Rule.parse_timeframe(test_str, tf_minutes)

    test_str = '3m2m'
    with pytest.raises(TimeframeArgDupeError):
        rule_meta.Rule.parse_timeframe(test_str, tf_minutes)

    test_str = '-4minute'
    assert rule_meta.Rule.parse_timeframe(test_str, tf_minutes) == -4

    test_str = '3h-4m+2M'
    assert rule_meta.Rule.parse_timeframe(test_str, tf_minutes) == -4
    assert rule_meta.Rule.parse_timeframe(test_str, tf_hours) == 3
    assert rule_meta.Rule.parse_timeframe(test_str, tf_months) == 2

    test_str = '''
            1minute
            2 hour
            3Day
            4w,5 mONths 6 y
            '''
    assert rule_meta.Rule.parse_timeframe(test_str, tf_minutes) == 1
    assert rule_meta.Rule.parse_timeframe(test_str, tf_hours) == 2
    assert rule_meta.Rule.parse_timeframe(test_str, tf_days) == 3
    assert rule_meta.Rule.parse_timeframe(test_str, tf_weeks) == 4
    assert rule_meta.Rule.parse_timeframe(test_str, tf_months) == 5
    assert rule_meta.Rule.parse_timeframe(test_str, tf_years) == 6
