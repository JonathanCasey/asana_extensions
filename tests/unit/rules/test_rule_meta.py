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

import pytest

from asana_extensions.general.exceptions import *   # pylint: disable=wildcard-import
from asana_extensions.rules import rule_meta



# @pytest.fixture(name='blank_rule')
# def fixture_blank_rule():
#     """
#     Makes a blank rule subclass of the abstract meta class so functionality can
#     be tested.

#     Returns:
#       (Rule<>): A subclass of the Rule metaclass with bare minimum defined.
#     """
#     class BlankRule(rule_meta.Rule):
#         """
#         Simple blank rule to subclass Rule.
#         """
#         @classmethod
#         def load_specific_from_config(cls, rules_cp, rule_id, **kwargs):
#             """
#             Not needed / will not be used.
#             """
#             return

#     return BlankRule('blank-rule-id', 'blank-rule-type', True)



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
