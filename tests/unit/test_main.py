#!/usr/bin/env python3
"""
Tests the asana_extensions.main functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
# pylint: disable=protected-access # Allow for purpose of testing those elements

import logging
import signal

import pytest

from asana_extensions import main
from asana_extensions import version
from asana_extensions.rules import rules as rules_mod



@pytest.fixture(autouse=True)
def fixture_ensure_logging_framework_not_altered():
    """
    This fixes an issue where some tests could fail when run together.  This is
    related to the StreamHandler use by the root logger in this project and
    `capsys`.

    Since `main.py` is the only place where the `_config_root_logger()` calls
    are made (at least one of those tests using `capsys`), this is the only test
    module that should need this.

    Thanks to gaborbernat for this code suggestion in a comment on
    [pytest-dev/pytest#14](https://github.com/pytest-dev/pytest/issues/14).
    """
    before_handlers = list(logging.getLogger().handlers)
    yield
    logging.getLogger().handlers = before_handlers



def test_global():
    """
    Tests items at the global scope not otherwise fully tested.
    """
    # Since only used (right now0 for logger name which is untested code, this
    #  gives the best chance of detecting a mistake there.
    assert main._NAME_MOD_OVERRIDE == 'asana_extensions.main'



def test_main(monkeypatch, caplog):
    """
    Tests the `main()` method.
    """
    def mock__main_rules(force_test_report_only=False):
        """
        Return true/false, but do so based on test report arg for convenience.
        """
        return force_test_report_only

    monkeypatch.setattr(main, '_main_rules', mock__main_rules)

    caplog.set_level(logging.INFO)

    caplog.clear()
    main.main(False, logging.WARNING, [])
    assert caplog.record_tuples == []

    caplog.clear()
    main.main(False, logging.INFO, [])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.INFO,
            'Asana Extensions had no modules to run -- fully skipped.'),
    ]

    caplog.clear()
    main.main(False, logging.INFO, None)
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.INFO,
            'Asana Extensions had no modules to run -- fully skipped.'),
    ]

    caplog.clear()
    main.main(False, logging.INFO, ['rules'])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.WARNING,
            'Asana Extensions run completed, but with errors...'),
    ]

    caplog.clear()
    main.main(True, logging.INFO, ['all'])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.INFO,
            'Asana Extensions run completed successfully!'),
    ]

    caplog.clear()
    main.main(False, 'bad log level', [])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.WARNING,
            "Logger setting failed (Exception: Unknown level: 'BAD LOG LEVEL')."
                + "  Defaulting to not set."),
        ('asana_extensions.main', logging.INFO,
            'Asana Extensions had no modules to run -- fully skipped.'),
    ]



def test__main_rules(monkeypatch, caplog):
    """
    Tests the `_main_rules()` method.
    """
    def mock_load_all_from_config_success(
                conf_rel_file='rules.conf'):   # pylint: disable=unused-argument
        """
        Return some simple items to use as return "rules".
        """
        return [-1, -2]

    def mock_load_all_from_config_failure(
                conf_rel_file='rules.conf'):   # pylint: disable=unused-argument
        """
        Return some simple items to use as return "rules".
        """
        return [-3, -4]

    def mock_execute_rules(rules, force_test_report_only=False):
        """
        Return True/False, but demonstrate args being used.
        """
        if force_test_report_only:
            rules_mod.logger.info('Test report only')
        if -3 in rules:
            return False
        return True

    monkeypatch.setattr(rules_mod, 'load_all_from_config',
            mock_load_all_from_config_success)
    monkeypatch.setattr(rules_mod, 'execute_rules', mock_execute_rules)

    caplog.set_level(logging.INFO)

    caplog.clear()
    assert main._main_rules(False) is True
    assert caplog.record_tuples == []

    caplog.clear()
    assert main._main_rules(True) is True
    assert caplog.record_tuples == [
        ('asana_extensions.rules.rules', logging.INFO, 'Test report only'),
    ]

    monkeypatch.setattr(rules_mod, 'load_all_from_config',
            mock_load_all_from_config_failure)

    caplog.clear()
    assert main._main_rules(False) is False
    assert caplog.record_tuples == []

    caplog.clear()
    assert main._main_rules(True) is False
    assert caplog.record_tuples == [
        ('asana_extensions.rules.rules', logging.INFO, 'Test report only'),
    ]



def test__config_root_logger(capsys):
    """
    Tests the `_config_root_logger()` method.
    """
    root_logger = logging.getLogger()
    assert root_logger.getEffectiveLevel() == logging.WARNING

    main._config_root_logger('info')
    assert root_logger.getEffectiveLevel() == logging.INFO

    main._config_root_logger(15)
    assert root_logger.getEffectiveLevel() == 15

    main._config_root_logger(10)
    assert root_logger.getEffectiveLevel() == logging.DEBUG

    main._config_root_logger('20')
    assert root_logger.getEffectiveLevel() == logging.INFO

    with pytest.raises(ValueError) as ex:
        main._config_root_logger('invalid-level')
    assert "Unknown level: 'INVALID-LEVEL'" in str(ex.value)

    class Dummy:                        # pylint: disable=too-few-public-methods
        """
        Dummy class that does nothing.
        """

    with pytest.raises(TypeError) as ex:
        main._config_root_logger(Dummy())
    assert 'Invalid log level type (somehow).  See --help for -l.' \
            in str(ex.value)

    main._config_root_logger(logging.DEBUG)
    main.logger.debug('debug log msg')
    main.logger.info('info log msg')
    main.logger.warning('warning log msg')
    main.logger.error('error log msg')
    stdmsg = capsys.readouterr()
    stdout = stdmsg.out
    stderr = stdmsg.err
    assert 'debug log msg' in stdout
    assert 'info log msg' in stdout
    assert 'warning log msg' not in stdout
    assert 'error log msg' not in stdout
    assert 'debug log msg' not in stderr
    assert 'info log msg' not in stderr
    assert 'warning log msg' in stderr
    assert 'error log msg' in stderr
    assert '<asana_extensions.main> DEBUG: debug log msg' in stdout
    assert '<asana_extensions.main> INFO: info log msg' in stdout
    assert '<asana_extensions.main> WARNING: warning log msg' in stderr
    assert '<asana_extensions.main> ERROR: error log msg' in stderr



def test__setup_and_call_main(monkeypatch, caplog, capsys):
    """
    Tests the `_setup_and_call_main()` method.
    """
    def mock_main(force_test_report_only, log_level, modules):
        """
        Since this is all about testing the values passed in to `main()`, this
        only needs to give some feedback on what each value was.
        """
        main.logger.info('Force test report only:'
                f' {str(force_test_report_only)}')
        main.logger.info(f'Log level: {str(log_level)}')
        if modules is None:
            main.logger.info(f'Modules: {str(modules)}')
        else:
            main.logger.info(f'Modules: `{"`|`".join(modules)}`')

    monkeypatch.setattr(main, 'main', mock_main)

    caplog.set_level(logging.INFO)

    main_mod_name = 'asana_extensions.main'

    with pytest.raises(SystemExit) as ex:
        main._setup_and_call_main('--unknown-arg'.split())
    assert str(ex.value) == '2'

    with pytest.raises(SystemExit) as ex:
        main._setup_and_call_main('-m'.split())
    assert str(ex.value) == '2'

    caplog.clear()
    main._setup_and_call_main(''.split())
    assert caplog.record_tuples == [
        (main_mod_name, logging.INFO, 'Force test report only: True'),
        (main_mod_name, logging.INFO, 'Log level: 30'),
        (main_mod_name, logging.INFO, 'Modules: None'),
    ]

    caplog.clear()
    main._setup_and_call_main("-e -l 20 -m 'bad-mod'".split())
    assert caplog.record_tuples == [
        (main_mod_name, logging.INFO, 'Force test report only: False'),
        (main_mod_name, logging.INFO, 'Log level: 20'),
        (main_mod_name, logging.INFO, "Modules: `'bad-mod'`"),
    ]

    caplog.clear()
    main._setup_and_call_main(
            '--modules rules all --log-level info --execute'.split())
    assert caplog.record_tuples == [
        (main_mod_name, logging.INFO, 'Force test report only: False'),
        (main_mod_name, logging.INFO, 'Log level: info'),
        (main_mod_name, logging.INFO, "Modules: `rules`|`all`"),
    ]

    caplog.clear()
    with pytest.raises(SystemExit) as ex:
        main._setup_and_call_main('--version'.split())
    assert caplog.record_tuples == []
    stdout, _ = capsys.readouterr()
    ver_parts = stdout.split('_')
    assert ver_parts[0] == 'asana'
    assert ver_parts[1] == f'extensions v{version._VERSION}'
    assert len(ver_parts) == 4



def test__register_shutdown_signals(monkeypatch, caplog):
    """
    Tests the `_register_shutdown_signals()` method.
    """
    def mock_shutdown(signum, _frame):
        """
        Instead of actually shutting down via sys.exit(), just log a message.
        """
        main.logger.warning(f'Would have exited from signal {str(signum)}')

    monkeypatch.setattr(main, '_shutdown', mock_shutdown)

    caplog.set_level(logging.DEBUG)

    hardcoded_signals = ['SIGINT', 'SIGTERM', 'SIGQUIT', 'SIGHUP']
    supported_signals = []
    default_handlers = {}
    for sig_name in hardcoded_signals:
        try:
            sig = getattr(signal, sig_name)
            default_handlers[sig] = signal.getsignal(sig)
            supported_signals.append(sig)
        except AttributeError:
            default_handlers[sig] = None

    main._register_shutdown_signals()
    for sig in supported_signals:
        assert signal.getsignal(sig) \
                == mock_shutdown      # pylint: disable=comparison-with-callable

    # Should be supported on all platforms but not one of the hardcoded
    test_signal = 'SIGSEGV'
    main._register_shutdown_signals([test_signal])
    assert signal.getsignal(getattr(signal, test_signal)) \
                == mock_shutdown      # pylint: disable=comparison-with-callable

    # Just make sure nothing implodes...should do nothing but log
    caplog.clear()
    bogus_signal = 'completely_bogus_signal'
    main._register_shutdown_signals([bogus_signal])
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.DEBUG,
            'Signal "completely_bogus_signal" not registered for shutdown.'
                + '  Likely not supported by this OS.'),
    ]



def test__shutdown(caplog):
    """
    Tests the `_shutdown()` method.

    ...might be best to keep this to the end of the file.  It seems some code
    intellisense doesn't like this handling of something that calls sys.exit()
    and will instead assume nothing else can possibly run.  After all, what
    comes after the end of the universe?
    """
    caplog.set_level(logging.WARNING)

    caplog.clear()
    with pytest.raises(SystemExit) as ex:
        main._shutdown(signal.SIGINT, None)
    assert '1' in str(ex.value)
    assert caplog.record_tuples == [
        ('asana_extensions.main', logging.WARNING,
            'Exiting from signal Signals.SIGINT ...'),
    ]
