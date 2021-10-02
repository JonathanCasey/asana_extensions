#!/usr/bin/env python3
"""
Move Tasks Rule functionality to implement the generic interface components
defined by the metaclass.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from asana_extensions.general import config
from asana_extensions.rules import rule_meta



logger = logging.getLogger(__name__)


# TODO: Check names and gids match when both given, including UTL
# TODO: If no include sections, default to include all except exclude


class MoveTasksRule(rule_meta.Rule):
    """
    Rules to move tasks to the specified destination based on the specified
    conditions.

    Class Attributes:
      N/A

    Instance Attributes:
      _rules_params ({str:str/int/bool/etc}): The generic dictionary that
        defines the parameters for this rule.

      [inherited from Rule]:
        _rule_id (str): The id used as the section name in the rules conf.
        _rule_type (str): The type of rule, such as "move tasks".
        _test_report_only (bool): Whether or not this is for reporting for
          testing only or whether rule is live.
    """
    def __init__(self, rule_params, **kwargs):
        """
        Create the Move Tasks Rule.

        Args:
          rules_params ({str:str/int/bool/etc}): The generic dictionary that
            defines the parameters for this rule.

          See parent(s) for required kwargs.

        Raises:
          (AssertionError): Invalid data.
        """
        super().__init__(**kwargs)

        is_project_given = rule_params['project_name'] is not None \
                or rule_params['project_gid'] is not None
        assert rule_params['is_my_tasks_list'] is False \
                or rule_params['user_task_list_gid'] is None, "Cannot" \
                    + " specify 'is my tasks list' and 'user task list gid'" \
                    + " together."
        is_user_task_list_given = rule_params['is_my_tasks_list'] \
                or rule_params['user_task_list_gid'] is not None
        assert is_project_given ^ is_user_task_list_given, "Must specify to" \
                + " use a project or user task list, but not both."
        assert rule_params['workspace_name'] is not None \
                or rule_params['workspace_gid'] is not None, "Must specify" \
                    + " workspace."

        is_time_given = rule_params['min_time_until_due_str'] is not None \
                or rule_params['max_time_until_due_str'] is not None
        is_time_parsed = rule_params['min_time_until_due'] is not None \
                or rule_params['max_time_until_due'] is not None
        assert is_time_given == is_time_parsed, "Failed to parse min/max" \
                + " time until due -- check format."
        assert is_time_given ^ rule_params['match_no_due_date'], "Must" \
                + " specify either min/max time until due or match no due" \
                + " date (but not both)."

        self._rule_params = rule_params



    @classmethod
    def load_specific_from_config(cls, rules_cp, rule_id, rule_params=None,
            **kwargs):
        """
        Loads the rule-specific config items for this rule from the
        configparsers from files provided.  Then creates the rule from the data
        provided and data loaded.

        Args:
          rule_cp (configparser): The full configparser from the rules conf.
          rule_id (str): The ID name for this rule as it appears as the
            section header in the rules_cp.
          rule_params ({str: str/int/bool/etc}): The rule parameters loaded from
            config.  Updated by super classes with their results.  Final sub
            class expected to be None.

          Note: kwargs contains other args to pass thru to constructor.

        Returns:
          rule (Rule<> or None): The Rule<> object created and loaded from
            config, where Rule<> is a subclass of Rule (e.g. MoveTasksRule).

        Raises:
          (AssertionError): Invalid data.
        """
        assert rule_params is None, "Should not pass anything in for" \
                + " `rule_params`"
        try:
            rule_params = {}
            super_params = {}
            super().load_specific_from_config(rules_cp, rule_id, super_params,
                    **kwargs)
            rule_params['project_name'] = rules_cp.get(rule_id, 'project name',
                    fallback=None)
            rule_params['project_gid'] = rules_cp.getint(rule_id, 'project gid',
                    fallback=None)
            rule_params['is_my_tasks_list'] = rules_cp.getboolean(rule_id,
                    'for my tasks list', fallback=None)
            rule_params['user_task_list_gid'] = rules_cp.getint(rule_id,
                    'user task list id', fallback=None)
            rule_params['workspace_name'] = rules_cp.get(rule_id,
                    'workspace name', fallback=None)
            rule_params['workspace_gid'] = rules_cp.getint(rule_id,
                    'workspace gid', fallback=None)

            rule_params['min_time_until_due_str'] = rules_cp.get(rule_id,
                    'min time until due', fallback=None)
            rule_params['min_time_until_due'] = cls.parse_timedelta_arg(
                    rule_params['min_time_until_due_str'])
            rule_params['max_time_until_due_str'] = rules_cp.get(rule_id,
                    'max time until due', fallback=None)
            rule_params['max_time_until_due'] = cls.parse_timedelta_arg(
                    rule_params['max_time_until_due_str'])
            rule_params['match_no_due_date'] = rules_cp.getboolean(rule_id,
                    'no due date', fallback=False)

            rule_params['src_sections_include_names'] = \
                    config.parse_list_from_conf_string(rules_cp.get(rule_id,
                        'src sections include names', fallback=None),
                        config.CastType.STRING, strip_quotes=True)
            rule_params['src_sections_include_gids'] = \
                    config.parse_list_from_conf_string(rules_cp.get(rule_id,
                        'src sections include gids', fallback=None),
                        config.CastType.INT)
            rule_params['src_sections_exclude_names'] = \
                    config.parse_list_from_conf_string(rules_cp.get(rule_id,
                        'src sections exclude names', fallback=None),
                        config.CastType.STRING, strip_quotes=True)
            rule_params['src_sections_exclude_gids'] = \
                    config.parse_list_from_conf_string(rules_cp.get(rule_id,
                        'src sections exclude gids', fallback=None),
                        config.CastType.INT)

            rule_params['dst_section_name'] = rules_cp.get(rule_id,
                    'dst section name', fallback=None)
            rule_params['dst_section_gid'] = rules_cp.getint(rule_id,
                    'dst section gid', fallback=None)

        except KeyError as ex:
            logger.error('Failed to parse Move Tasks Rule from config.  Check'
                    + f' keys.  Exception: {str(ex)}')
            raise

        try:
            rule = cls(rule_params, **kwargs, **super_params, rule_id=rule_id)
            return rule
        except AssertionError as ex:
            logger.error(f'Failed to create Move Tasks Rule from config: {ex}')
            return None



    @classmethod
    def get_rule_type_names(cls):
        """
        Get the list of names that can be used as the 'rule type' in the rules
        conf to identify this rule.

        Returns:
          ([str]): A list of names that are valid to use as the type for this
            rule.
        """
        return ['move tasks', 'auto-promote tasks', 'auto-promote',
                'auto promote tasks', 'auto promote', 'promote tasks']
