#!/usr/bin/env python3
"""
General utility functions for the project that do not fit in another other
more-specific sub-package.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import datetime as dt

from dateutil.relativedelta import relativedelta



def is_date_only(dt_var):
    """
    Check whether the provided variable is a date-only format provided that
    format is supported.

    This does NOT rely on hack methods of checking such as looking a datetime
    object having 0 for hours and minutes since that could be the same as a
    datetime at midnight.

    Args:
      dt_var (relativedelta/str): A datetime variable that may be a date, time,
        or datetime.  Supported types and formats are:
          - relativedelta
          - ISO 8601 string

    Returns:
      (bool): True if definitely a date only; False if definitely a time or
        datetime.

    Raises:
      (NotImplementedError): The type or format of the provided `dt_var` arg is
        not supported.
    """
    if isinstance(dt_var, relativedelta):
        # Inspired by logic check for relativedelta._has_time in source:
        # https://dateutil.readthedocs.io/en/stable/_modules/dateutil/relativedelta.html
        return (not dt_var.hours and not dt_var.minutes and not dt_var.seconds
                and not dt_var.microseconds)

    try:
        dt.date.fromisoformat(dt_var)
        return True
    except ValueError:
        try:
            dt.datetime.fromisoformat(dt_var)
            return False
        except ValueError:
            # Not an ISO date nor time -- fall thru to check other types
            pass
    except TypeError:
        # Not a string to try ISO date/time -- fall thru to check other types
        pass

    raise NotImplementedError('Datetime format provided to `is_date_only()`'
            + f' is not supported at this time: {dt_var}')
