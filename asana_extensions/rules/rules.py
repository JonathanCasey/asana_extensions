#!/usr/bin/env python3
"""
The rules API module.  This is intended to be the item accessed outside of
the rules submodule/folder.

Module Attributes:

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



def load_all_from_config():
    """
    Loads all rules from the rules config file.

    Returns:
      loaded rules ([Rule<>]): Returns list of rules successfully loaded from
        rules config file.
    """
    loaded_rules = []
    rules_cp = config.read_conf_file('rules.conf')
    for rule_id in rules_cp.sections():
        kwargs = {}
        kwargs['rule_id'] = rule_id.strip()
        kwargs['rule_type'] = rules_cp[rule_id]['rule type'].strip()
        kwargs['test_report_only'] = rules_cp.getboolean(rule_id,
                'test report only', fallback=False)

        for rule_cls in _RULES:
            if kwargs['rule_type'] in rule_cls.get_rule_type_names():
                new_rule = rule_cls.load_specific_from_conf(rules_cp, **kwargs)
                if new_rule is not None:
                    loaded_rules.append(new_rule)
                else:
                    logger.warning('Matched rule type but failed to parse'
                            + f'for rules.conf section "{rule_id}"')

    return loaded_rules
