#!/usr/bin/env python3
"""This module lists all user defined exceptions for import to the modules
that need them (in alphabetical order).

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""



class TimeframeArgDupeError(Exception):
    """
    Raised when parsing a timedelta config argument and one of the timeframe
    parameters (e.g. days) is duplicated within the same arg.
    """
