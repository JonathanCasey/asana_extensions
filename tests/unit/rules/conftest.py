#!/usr/bin/env python3
"""
Configures pytest as needed.  This file normally does not need to exist, but is
used here to share and configure items for the /tests/unit/rules subpackage.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import pytest

from asana_extensions.rules import rule_meta



@pytest.fixture(name='blank_rule_cls')
def fixture_blank_rule_cls():
    """
    Returns a blank rule with default returns for all abstract methods.  This
    can be used as is in most cases; in most other cases, this can serve as a
    base with tests only needing to override individual methods via monkeypatch.
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

        def _sync_and_validate_with_api(self):
            """
            Not needed / will not be used.
            """
            return True

        def execute(self, force_test_report_only=False):
            """
            Not needed / will not be used.
            """
            return True

    return BlankRule
