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

        new_rule_cls = None
        for rule_cls in _RULES:
            if rule_type in rule_cls.get_rule_type_names():
                new_rule_cls = rule_cls
                break

        if new_rule_cls is None:
            logger.warning('Failed to match any rule type for rules.conf'
                    + f' section "{rule_id}"')
        else:
            new_rule = new_rule_cls.load_specific_from_conf(rules_cp, rule_id)
            if new_rule is not None:
                loaded_rules.append(new_rule)
            else:
                logger.warning('Matched rule type but failed to parse'
                        + f' for rules.conf section "{rule_id}"')

    return loaded_rules
