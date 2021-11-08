#!/usr/bin/env python3
"""This module lists all user defined exceptions for import to the modules
that need them (in alphabetical order).  These are only intended to be used
within the test modules, not in the actual project/module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""



class TesterNotInitializedError(Exception):
    """
    Raised when tests cannot be run because some required external setup is not
    complete.
    """
