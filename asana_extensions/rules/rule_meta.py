#!/usr/bin/env python3
"""
This module handles access to the configuration files.  The configuration
files--including the environment files--are accessed by the other python scripts
through this file.

This is setup such that other files need only call the `get()` functions, and
all the loading and caching will happen automatically internal to this file.

As of right now, this is hard-coded to access configuration files at a specific
name and path.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC, abstractmethod
import datetime as dt
import logging
import re
import string

from dateutil.relativedelta import relativedelta

from asana_extensions.general import config
from asana_extensions.general.exceptions import *   # pylint: disable=wildcard-import



logger = logging.getLogger(__name__)



class Rule(ABC):
    """
    The abstract class for all automation rule functionality.  Each rule type
    will subclass this, but externally will likely only call the generic methods
    defined here to unify the interface.

    This serves as a base class for other rules, so will consume any final
    kwargs.

    Class Attributes:
      N/A

    Instance Attributes:
      _rule_id (str): The id used as the section name in the rules conf.
      _rule_type (str): The type of rule, such as "move tasks".
      _test_report_only (bool): Whether or not this is for reporting for
        testing only or whether rule is live.
      _is_valid (bool or None): Cached value as to whether the rule is valid.
        If not validated yet, will be None.
    """
    def __init__(self, rule_id, rule_type, test_report_only, **kwargs):
        """
        Creates the rule.

        Args:
          rule_id (str): The id used as the section name in the rules conf.
          rule_type (str): The type of rule, such as "move tasks".
          test_report_only (bool): Whether or not this is for reporting for
            testing only or whether rule is live.
          kwargs ({}): Should be empty since this is the base class.  Will log
            warning if not empty.
        """
        self._rule_id = rule_id
        self._rule_type = rule_type
        self._test_report_only = test_report_only

        if kwargs:
            logger.warning('Discarded excess kwargs provided to'
                    + f' {self.__class__.__name__}: {", ".join(kwargs.keys())}')

        self._is_valid = None



    @classmethod
    @abstractmethod
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
          (KeyError): Missing critical config keys.
        """
        assert rule_params is not None, "Subclass must provide `rule_params`."
        try:
            rule_params['rule_type'] = rules_cp[rule_id]['rule type']
            rule_params['test_report_only'] = rules_cp.getboolean(rule_id,
                    'test report only', fallback=None)
        except KeyError as ex:
            logger.error('Failed to parse Rule from config.  Check keys.'
                    + f'  Exception: {str(ex)}')
            raise
        except ValueError as ex:
            logger.error('Failed to parse Rule from config.  Check strong typed'
                    + f' values.  Exception: {str(ex)}')
            raise



    def get_rule_id(self):
        """
        Get the id/name of this rule.

        Returns:
          _rule_id (str): The ID or name of this rule.
        """
        return self._rule_id



    @classmethod
    @abstractmethod
    def get_rule_type_names(cls):
        """
        Get the list of names that can be used as the 'rule type' in the rules
        conf to identify this rule.

        Returns:
          ([str]): A list of names that are valid to use as the type for this
            rule.
        """



    @abstractmethod
    def _sync_and_validate_with_api(self):
        """
        Sync configuration data with the API and further validate, storing any
        newly prepared configuration info.  This is largely a contintuation
        of __init__() where API-dependent items can be completed in case it is
        ideal to decouple the API access from __init__().

        Returns:
          (bool): True if completed successfully; False if failed for any
            reason (this should probably catch nearly all exceptions).
        """



    def is_valid(self):
        """
        Check whether this rule is valid or not.  This ideally utilizes a cached
        value so that the check for being valid does not need to be done more
        than once since that could involve heavy API access.  As a result, it is
        likely that this should call `_sync_and_validate_with_api()`.  In most
        cases, can just rely on the logic in this metaclass.

        Returns:
          (bool): True if is valid; False if invalid.
        """
        if self._is_valid is None:
            self._is_valid = self._sync_and_validate_with_api()
        return self._is_valid



    def is_criteria_met(self):                     # pylint: disable=no-self-use
        """
        Checks whether the criteria to run this rule, if any, has been met.  If
        any additional processing is required for this, it should be done and
        stored as appropriate.  In such a case, it may be advisable to cache
        the overall result.

        Where possible, this should be decoupled from `is_valid()`, but in many
        cases it will likely make sense for this to only run if `is_valid()` is
        True.  Hence, this may get masked by that result in those cases.

        Some rules do not have any specific criteria as to whether the rule
        should run (e.g. no specific datetime at which it should run if script
        expected to be called multiple times), in which case this should just
        return True.

        If a rule does need to implement a criteria check, this should be
        overridden.

        Returns:
          (bool): True if criteria is met for rule to run or there is no
            criteria (i.e. this is not applicable); False if not ready to run.
        """
        return True



    @abstractmethod
    def execute(self, force_test_report_only=False):
        """
        Execute the rule.  This should likely check if it is valid and the
        criteria to run the rule has been met (if any).  If either the rule is
        set to test report only or the caller of this method specified to force
        to be test report only, no changes will be made via the API -- only
        simulated results will be reported (but still based on data from API).

        This should ideally catch all errors except ones so catastrophic that
        the operation of the entire app should cease immediately.  Callers of
        this method are not intended to require try/except handling for things
        like mis-configured rules, etc.

        Args:
          force_test_report_only (bool): If True, will ensure this runs as a
            test report only with no changes made via the API; if False, will
            defer to the `_test_report_only` setting of the rule.

        Returns:
          (bool): True if fully completed without any errors; False any errors,
            regardless of whether it resulted in partial or full failure.
        """



    @classmethod
    def parse_time_arg(cls, t_str, is_tz_required=False):
        """
        Parses a simple ISO format time string.  This does NOT have exhaustive
        ISO 8601 format.

        Args:
          t_str (str or None): The string to parse a time value.  None allowed
            for convenience.
          is_tz_allowed (bool or None): Whether the time string is required to
            have timezone information.  True and False mean required and not
            required, respectively.  If None, it is required that the timezone
            is NOT provided at all.

        Returns:
          time_parsed (time or None): The time object parsed from the time
            string provided, with the timezone enforced as specified.  If None
            or empty string provided, None returned.

        Raises:
          (config.UnsupportedFormatError): Raised if timezone information is
            incompatible between the time string provided and the timezone
            requirement specified.  Specifically, this is raised if timezone is
            required and there is no timezone parsed from the string; or if
            timezone is prohibited (None) and there is a timezone parsed from
            the string.
          (ValueError): Raised if not a valid ISO format time string.
        """
        assert is_tz_required is True or is_tz_required is False \
                or is_tz_required is None, \
                '`is_tz_required` must be bool or None'

        if t_str is None or t_str == '':
            return None

        time_parsed = dt.time.fromisoformat(t_str)
        if is_tz_required is True and time_parsed.tzinfo is None:
            raise config.UnsupportedFormatError('Timezone required for time'
                    + f" string, but none found.  String: '{t_str}',"
                    + f' parsed: `{time_parsed}`')
        if is_tz_required is None and time_parsed.tzinfo is not None:
            raise config.UnsupportedFormatError('Timezone prohibited for time'
                    + f" string, but one was provided.  String: '{t_str}',"
                    + f' parsed: `{time_parsed}`')
        return time_parsed



    @classmethod
    def parse_timedelta_arg(cls, arg_str):
        """
        Parses a timedelta argument as might be specified in a config file.

        Possible timeframes to specify (with case-sensitive abbreviations in
        parentheses) are:
          (m) minutes
          (h) hours
          (d) days
          (w) weeks
          (M) Months
          (y) years
        Shortnames are case sensitive; full names are not.

        Months and years will be converted per dateutils.relativedelta's
        handling.  If ever changed, the intention will be that months and years
        will be converted to days with respect to today.  If used in combination
        with other items, such as days, those will be added AFTER converting
        months/years to days.

        Args:
          arg_str (str or None): The string to parse.  Can be None for caller's
                convenience.

        Returns:
          (relativedelta or None): The relative datetime delta specified by the
                string.  If None or empty string passed in, None is returned.

        Raises:
          Will pass thru any exceptions raised from timeframe parser.
        """
        if arg_str is None or arg_str == '':
            return None

        kwargs = {}
        kwargs['minutes'] = cls.parse_timeframe(arg_str,
                {'minutes?': False, 'm': True})
        kwargs['hours'] = cls.parse_timeframe(arg_str,
                {'hours?': False, 'h': True})
        kwargs['days'] = cls.parse_timeframe(arg_str,
                {'days?': False, 'd': True})
        kwargs['weeks'] = cls.parse_timeframe(arg_str,
                {'weeks?': False, 'w': True})
        kwargs['months'] = cls.parse_timeframe(arg_str,
                {'months?': False, 'M': True})
        kwargs['years'] = cls.parse_timeframe(arg_str,
                {'years?': False, 'y': True})

        return relativedelta(**kwargs)



    @classmethod
    def parse_timeframe(cls, tf_str, timeframes):
        """
        Parses a specific timeframe indicator from a string.  A collection of
        possible ways that timeframe can be specified can be given in regex
        format (must be string Template compatible).  Each can specify whether
        case sensitive or not.

        Exactly 1 match is expected.  If no matches, will return nothing; but
        more than 1 is considered an error condition.

        Args:
          tf_str (str): The string to search for timeframe indicators.
          timeframes ({str:bool}): Timeframe indicators to search in string,
            where the regex strings to search are the keys and the bool value
            is whether or not it is case sensitive (True == case sensitive).

        Returns:
          (int): The number specified with the timeframe if exactly 1 match
            found; 0 if no matches.

        Raises:
          (TimeframeArgDupeError): More than 1 match found.
        """
        # Pattern is generally:
        #   Start of line; or whitespace, letter, or comma (look behind)
        #   Possible plus/neg sign and definitely digits
        #   Possible 1 whitespace
        #   <letter or word> depending on time keyword, word could have s at end
        #   Whitespace, neg/plus sign, digit, comma, or end of line
        #         (without consuming)
        # Note double $$ used for end of line since written as Template
        ptn_template = string.Template(r'(^|(?<=\s|[a-z]|[A-Z]|,))'
                + r'(?P<num>(\+|-)?\d+)\s?' + '$timeframe'
                + r'(?=\s|-|\d|,|\+|$$)')

        ptns = []
        for timeframe, case_sensitive in timeframes.items():
            regex_str = ptn_template.substitute(timeframe=timeframe)
            if case_sensitive:
                ptn = re.compile(regex_str, re.MULTILINE)
            else:
                ptn = re.compile(regex_str, re.MULTILINE | re.IGNORECASE)
            ptns.append(ptn)

        matches = []
        for ptn in ptns:
            matches.extend(ptn.finditer(tf_str))

        if len(matches) == 0:
            return 0

        if len(matches) > 1:
            '/'.join(timeframes.keys())
            raise TimeframeArgDupeError('Could not parse time frame - Found'
                    + f' {len(matches)} entries for'
                    + f' {"/".join(timeframes.keys())} when only 0-1 allowed.')

        return int(matches[0].group('num'))
