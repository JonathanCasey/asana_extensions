#!/usr/bin/env python3
"""
The main entry point for the package.

Module Attributes:
  _NAME_MOD_OVERRIDE (str): Name to use as override for `__name__` in select
    cases since, in this module, `__name__` is often expected to be `__main__`.
  logger (Logger): Logger for this module.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import argparse
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



def main(force_test_report_only, log_level, modules):
    """
    Launches the main app.

    Args:
      force_test_report_only (bool): True to force test report only mode; False
        to allow full execution (pending other settings).
      log_level (Level/int/str): The desired log level.  This can be specified
        as a level constant from the logging module, or it can be an int or str
        reprenting the numeric value (possibly as a str) or textual name
        (possibly with incorrect case) of the level.
      modules ([str]): The list of module names of what to execute.  See the
        arg parsing code in `_setup_and_call_main()` for details of options.
    """
    _config_root_logger(log_level)
    any_errors = None

    if any(x.lower() in ['rules', 'all'] for x in modules):
        any_errors = not _main_rules(force_test_report_only) \
                or any_errors or False

    if any_errors is None:
        logger.info('Asana Extensions had no modules to run -- fully skipped.')
    elif any_errors:
        logger.warning('Asana Extensions run completed, but with errors...')
    else:
        logger.info('Asana Extensions run completed successfully!')



def _main_rules(force_test_report_only):
    """
    The main function for execution the rules modules.

    Args:
      force_test_report_only (bool): True to force test report only mode; False
        to allow full execution (pending other settings).

    Return:
      (bool): True if fully successful (even in test report only mode); False if
        any errors occurred that partially or fully prevented completion.
    """
    all_rules = rules.load_all_from_config()
    return rules.execute_rules(all_rules, force_test_report_only)



def _config_root_logger(log_level):
    """
    Configure the root logger.

    Specifically, this sets the log level for the root logger so it will apply
    to all loggers in this app.

    Args:
      log_level (Level/int/str): The desired log level.  This can be specified
        as a level constant from the logging module, or it can be an int or str
        reprenting the numeric value (possibly as a str) or textual name
        (possibly with incorrect case) of the level.

    Raises:
      (TypeError): Invalid type provided for `log_level`.
      (ValueError): Correct type provided for `log_level`, but is not a valid
        supported value.
    """
    root_logger = logging.getLogger() # Root logger will config app-wide

    try:
        root_logger.setLevel(log_level.upper())
        return
    except AttributeError:
        # Likely passed in an int, which has no method `upper()` -- retry below
        pass
    # ValueError is probably an "unknown level" from logger -- let it be raised

    try:
        root_logger.setLevel(int(log_level))
        return
    except ValueError:
        # Probably an invalid type that couldn't be cast -- let fall thru
        pass

    raise TypeError('Invalid log level type (somehow).  See --help for -l.')



def _setup_and_call_main(_args=None):
    """
    Setup any pre-main operations, such as signals and input arg parsing, then
    call `main()`.  This is basically what would normally be in
    `if __name__ == '__main__':` prior to `main()` call, but this allows unit
    testing a lot more easily.

    Args:
      _args ([str] or None): The list of input args to parse.  Should only be
        used by unit testing.  When executing, it is expected this stays as
        `None` so it will default to taking args from `sys.argv` (i.e. from
        CLI).
    """
    _register_shutdown_signals()

    parser = argparse.ArgumentParser(description='Process inputs.')
    parser.add_argument('-e', '--execute',
            dest='force_test_report_only',
            action='store_const',
            const=False,
            default=True,
            help='Execute the module(s).  Without this, it will run in test'
                + ' report only mode.')
    parser.add_argument('-l', '--log_level',
            default=logging.WARNING,
            help='Set the log level through the app.  Will only report logged'
                + ' messages that are the specified level or more severe.'
                + '  Defaults to "Warning".  Can specify by name or number to'
                + ' match python `logging` module: notset/0, debug/10, info/20,'
                + ' warning/30, error/40, critical/50.')
    parser.add_argument('-m', '--modules',
            nargs='+',
            help='The modules to run in this invocation.  Required.  Can'
                + ' specify "all" to run all modules.  Otherwise, can provide a'
                + ' space-separate list of module names.  Supported modules:'
                + ' rules.')

    main(**vars(parser.parse_args(_args)))



def _register_shutdown_signals(signals=None):
    """
    Registers the shutdown signals that will be supported, handling any platform
    dependent discrepancies gracefully.

    Args:
      signals ([str] or None): String of names of signals in `signal` module, or
        `None` to use defaults.
    """
    if signals is None:
        signals = ('SIGINT', 'SIGTERM', 'SIGQUIT', 'SIGHUP')

    for sig in signals:
        try:
            signal.signal(getattr(signal, sig), _shutdown)
        except AttributeError:
            # Likely a platform didn't support one of the options
            continue



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
