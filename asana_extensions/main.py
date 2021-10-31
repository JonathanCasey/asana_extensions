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
import signal
import sys

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



def _setup_and_call_main():
    """
    Setup any pre-main operations, such as signals and input arg parsing, then
    call `main()`.  This is basically what would normally be in
    `if __name__ == '__main__':` prior to `main()` call, but this allows unit
    testing a lot more easily.
    """
    for sig in ('INT', 'TERM', 'QUIT', 'HUP'):
        signal.signal(getattr(signal, 'SIG%s' % sig), _shutdown)

    main()



def _shutdown(signum, _frame):
    """
    Perform all necessary operations to cleanly shutdown when required.

    This is triggered through signal interrupts as registered when this is
    executed as a script.

    Args:
      signum (int): Number of signal received.
      _frame (frame): See signal.signal python docs.
    """
    msg = f'Exiting from signal {str(signum)} ...'
    logger.warning(msg)
    sys.exit(1)



if __name__ == '__main__':                                  # Ignored by CodeCov
    # Since no unit testing here, code kept at absolute minimum
    _setup_and_call_main()
