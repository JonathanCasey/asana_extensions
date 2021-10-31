#!/usr/bin/env python3
"""
The rules API module.  This is intended to be the item accessed outside of
the rules submodule/folder.

Module Attributes:
  logger (Logger): Logger for this module.
  _RULES ((Class<Rule<>>)): All rule classes supported.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from asana_extensions.general import config
from asana_extensions.rules import move_tasks_rule



logger = logging.getLogger(__name__)

_RULES = {
    move_tasks_rule.MoveTasksRule,
}



def load_all_from_config(conf_rel_file='rules.conf'):
    """
    Loads all rules from the rules config file.

    Args:
      conf_rel_file (str): The config file from which to load all rules.  Can
        omit to use default rule file name.

    Returns:
      loaded rules ([Rule<>]): Returns list of rules successfully loaded from
        rules config file.
    """
    loaded_rules = []
    rules_cp = config.read_conf_file(conf_rel_file)
    for rule_id in rules_cp.sections():
        rule_id = rule_id.strip()
        rule_type = rules_cp.get(rule_id, 'rule type', fallback='').strip()

        is_rule_type_valid = False
        for rule_cls in _RULES:
            if rule_type in rule_cls.get_rule_type_names():
                is_rule_type_valid = True
                new_rule = rule_cls.load_specific_from_conf(rules_cp, rule_id)
                break

        if not is_rule_type_valid:
            logger.warning('Failed to match any rule type for rules.conf'
                    + f' section "{rule_id}"')
        elif new_rule is None:
            logger.warning('Matched rule type but failed to parse for'
                    + f' rules.conf section "{rule_id}"')
        else:
            loaded_rules.append(new_rule)

    return loaded_rules



def execute_rules(rules, force_test_report_only=False):
    """
    Execute all provided rules.  If either an individual rule is set to test
    report only or the caller of this method specified to force to be test
    report only, no changes will be made via the API for that rule -- only
    simulated results will be reported (but still based on data from API).

    Args:
      force_test_report_only (bool): If True, will ensure this runs as a test
        report only with no changes made via the API for all rules; if False,
        will defer to the `_test_report_only` setting of each rule.

    Returns:
      (bool): True if fully completed without any errors; False any errors,
        regardless of whether it resulted in partial or full failure.
    """
    any_errors = False
    for rule in rules:
        any_errors = rule.execute(force_test_report_only) or any_errors
    return not any_errors
