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
import logging
import re
import string

from dateutil.relativedelta import relativedelta

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



    @classmethod
    @abstractmethod
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
          rule (Rule<>): The Rule<> object created and loaded from config, where
            Rule<> is a subclass of Rule (e.g. MoveTasksRule).

        Raises:
          (AssertionError): Invalid data.
        """
        assert rule_params is not None
        try:
            rule_params['rule_type'] = rules_cp[rule_id]['rule type']
            rule_params['test_report_only'] = rules_cp.getboolean(rule_id,
                    'test report only', fallback=None)
        except KeyError as ex: # TODO: Update exception type
            logger.error('Failed to parse Rule from config.  Check keys.'
                    + f'  Exception: {str(ex)}')
            raise



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
          arg_str (str): The string to parse

        Returns:
          (relativedelta): The relative datetime delta specified by the string.

        Raises:
          Will pass thru any exceptions raised from timeframe parser.
        """
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
