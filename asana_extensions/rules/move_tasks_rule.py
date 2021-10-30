#!/usr/bin/env python3
"""
Move Tasks Rule functionality to implement the generic interface components
defined by the metaclass.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

import asana

from asana_extensions.asana import client as aclient
from asana_extensions.asana import utils as autils
from asana_extensions.general import config
from asana_extensions.general.exceptions import *   # pylint: disable=wildcard-import
from asana_extensions.rules import rule_meta



logger = logging.getLogger(__name__)



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
        _is_valid (bool or None): Cached value as to whether the rule is valid.
          If not validated yet, will be None.
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
                    + " specify 'for my tasks list' and 'user task list gid'" \
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
    def load_specific_from_conf(cls, rules_cp, rule_id, rule_params=None,
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
            Will return None if failed to load and create due to invalid config.
            Abstract parent classes such as Rule will return None.

        Raises:
          (AssertionError): Invalid data.
        """
        assert rule_params is None, "Should not pass anything in for" \
                + " `rule_params`"
        try:
            rule_params = {}
            super_params = {}
            super().load_specific_from_conf(rules_cp, rule_id, super_params,
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

            rule_params['match_no_due_date'] = rules_cp.getboolean(rule_id,
                    'no due date', fallback=False)
            rule_params['min_time_until_due_str'] = rules_cp.get(rule_id,
                    'min time until due', fallback=None)
            rule_params['min_time_until_due'] = cls.parse_timedelta_arg(
                    rule_params['min_time_until_due_str'])
            rule_params['max_time_until_due_str'] = rules_cp.get(rule_id,
                    'max time until due', fallback=None)
            rule_params['max_time_until_due'] = cls.parse_timedelta_arg(
                    rule_params['max_time_until_due_str'])
            rule_params['min_due_assumed_time_str'] = rules_cp.get(rule_id,
                    'assumed time for min due', fallback=None)
            rule_params['min_due_assumed_time'] = cls.parse_time_arg(
                    rule_params['min_due_assumed_time_str'], None)
            rule_params['max_due_assumed_time_str'] = rules_cp.get(rule_id,
                    'assumed time for max due', fallback=None)
            rule_params['max_due_assumed_time'] = cls.parse_time_arg(
                    rule_params['max_due_assumed_time_str'], None)

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

        except config.UnsupportedFormatError as ex:
            logger.error('Failed to parse Move Tasks Rule from config.  Check'
                    + f' time args.  Exception: {str(ex)}')
            return None
        except KeyError as ex:
            logger.error('Failed to parse Move Tasks Rule from config.  Check'
                    + f' keys.  Exception: {str(ex)}')
            return None
        except TimeframeArgDupeError as ex:
            logger.error('Failed to parse Move Tasks Rule from config.  Check'
                    + f' timeframe args.  Exception: {str(ex)}')
            return None
        except ValueError as ex:
            logger.error('Failed to parse Move Tasks Rule from config.  Check'
                    + f' strong typed values.  Exception: {str(ex)}')
            return None

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
        # pylint: disable=multi-line-list-first-line-item
        # pylint: disable=multi-line-list-eol-close, closing-comma
        return ['move tasks', 'auto-promote tasks', 'auto-promote',
                'auto promote tasks', 'auto promote', 'promote tasks']



    def _sync_and_validate_with_api(self):
        """
        Sync configuration data with the API and further validate, storing any
        newly prepared configuration info.

        Returns:
          (bool): True if completed successfully; False if failed for any
            reason (this should probably catch nearly all exceptions).
        """
        rps = self._rule_params # Shorten name since used so much here
        try:
            if rps['workspace_name'] is not None:
                rps['workspace_gid'] = aclient.get_workspace_gid_from_name(
                            rps['workspace_name'], rps['workspace_gid'])

            if rps['is_my_tasks_list']:
                rps['user_task_list_gid'] = aclient.get_user_task_list_gid(
                        rps['workspace_gid'], True)

            if rps['project_name'] is not None:
                # For now, hardcoded for non-archived project
                #   Could use None, but workaround for now is to specify by gid
                rps['project_gid'] = aclient.get_project_gid_from_name(
                        rps['workspace_gid'], rps['project_name'],
                        rps['project_gid'])
                rps['effective_project_gid'] = rps['project_gid']

            elif rps['user_task_list_gid'] is not None:
                rps['effective_project_gid'] = rps['user_task_list_gid']

            # Else, shouldn't be possible based on assertions in __init__()

            # Always want to default to include for move task rule
            rps['src_net_include_section_gids'] = \
                    autils.get_net_include_section_gids(
                            rps['effective_project_gid'],
                            rps['src_sections_include_names'],
                            rps['src_sections_include_gids'],
                            rps['src_sections_exclude_names'],
                            rps['src_sections_exclude_gids'])

            if rps['dst_section_name'] is not None:
                rps['dst_section_gid'] = aclient.get_section_gid_from_name(
                        rps['effective_project_gid'], rps['dst_section_name'],
                        rps['dst_section_gid'])

        except (asana.error.AsanaError, aclient.ClientCreationError,
                aclient.DataNotFoundError, aclient.DuplicateNameError,
                aclient.MismatchedDataError, autils.DataConflictError,
                autils.DataMissingError) as ex:
            logger.error(f'Failed to sync and validate rule "{self._rule_id}"'
                    + f' with the API.  Skipping rule.  Exception: {str(ex)}')
            return False

        return True



    def execute(self, force_test_report_only=False):
        """
        Execute the rule.  This should likely check if it is valid and the
        criteria to run the rule has been met (if any).  If either the rule is
        set to test report only or the caller of this method specified to force
        to be test report only, no changes will be made via the API -- only
        simulated results will be reported (but still based on data from API).

        Args:
          force_test_report_only (bool): If True, will ensure this runs as a
            test report only with no changes made via the API; if False, will
            defer to the `_test_report_only` setting of the rule.
        """
        if not self.is_valid() or not self.is_criteria_met():
            return

        rps = self._rule_params # Shorten name since used so much here
        tasks_to_move = []
        for src_sect_gid in rps['src_net_include_section_gids']:
            # Could lock in a dt_base before loop, but likely not an issue
            # For now, hardcoded for incomplete tasks
            tasks_to_move.extend(autils.get_filtered_tasks(src_sect_gid,
                    rps['match_no_due_date'],
                    rps['min_time_until_due'], rps['max_time_until_due'],
                    rps['min_due_assumed_time'], rps['max_due_assumed_time']))

        for task in tasks_to_move[::-1]:
            # For now, hardcoded to move to top, maintaining order
            if self._test_report_only or force_test_report_only:
                msg = '[Test Report Only] For MoveTasksRule'
                msg += f' "{self._rule_id}", would have moved task'
                msg += f' "{task["name"]}" [{task["gid"]}]'
                msg += ' to top of section'
                if rps['dst_section_name'] is not None:
                    msg += f' "{rps["dst_section_name"]}"'
                msg += f' [{rps["dst_section_gid"]}].'
                logger.info(msg)
            else:
                aclient.move_task_to_section(task['gid'],
                        rps['dst_section_gid'])
