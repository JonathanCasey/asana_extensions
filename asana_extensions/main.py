#!/usr/bin/env python3
"""
The main entry point for the package.

Module Attributes:
  _NAME_MOD_OVERRIDE (str): Name to use as override for `__name__` in select
    cases since, in this module, `__name__` is often expected to be `__main__`.
  logger (Logger): Logger for this module.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from asana_extensions.rules import rules



_NAME_MOD_OVERRIDE = 'asana_extensions.main'

if __name__ == '__main__':                                  # Ignored by CodeCov
    # Since no unit testing here, code kept at absolute minimum
    logger = logging.getLogger(_NAME_MOD_OVERRIDE)
else:
    logger = logging.getLogger(__name__)



def main():
    """
    Launches the main app.
    """
    all_rules = rules.load_all_from_config()
    rules.execute_rules(all_rules)



if __name__ == '__main__':                                  # Ignored by CodeCov
    # Since no unit testing here, code kept at absolute minimum
    main()
