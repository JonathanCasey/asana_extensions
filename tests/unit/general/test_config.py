"""
Tests the grand_trade_auto.general.config functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging
import os.path

import pytest

from asana_extensions.general import config
from asana_extensions.general import dirs



@pytest.fixture(name='mock_get_conf_path')
def fixture_mock_get_conf_path():
    """
    A mock function to monkeypatch in to use the test config path.

    Returns:
      (method): Returns a method that will mock getting the conf path.  Intended
        to be monkeypatched in for the equivalent method in dirs.
    """
    def mock_dirs_get_conf_path():
        """
        Get the test dir's conf path.
        """
        this_dir = os.path.dirname(os.path.realpath(__file__))
        conf_dir = os.path.join(this_dir, 'test_config')
        return conf_dir

    return mock_dirs_get_conf_path



def test_read_conf_file_fake_header(mock_get_conf_path, monkeypatch):
    """
    Tests that the `read_conf_file_fake_header()` will correctly read a file
    with no header, regardless of whether a fake header name was provided or the
    default was used.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_config')
    parser = config.read_conf_file_fake_header('mock_config_no_header.conf',
            conf_dir)
    assert parser['fake']['test key no header'] == 'test-val-no-header'
    assert parser['test-section']['test key str'] \
            == 'test-val-str'

    parser = config.read_conf_file_fake_header('mock_config_no_header.conf',
            conf_dir, 'new fake')
    assert parser['new fake']['test key no header'] == 'test-val-no-header'
    assert parser['test-section']['test key str'] \
            == 'test-val-str'

    monkeypatch.setattr(dirs, 'get_conf_path', mock_get_conf_path)
    parser = config.read_conf_file_fake_header('mock_config_no_header.conf')
    assert parser['fake']['test key no header'] == 'test-val-no-header'
    assert parser['test-section']['test key str'] \
            == 'test-val-str'



def test_read_conf_file(mock_get_conf_path, monkeypatch):
    """
    Tests that the `read_conf_file()` will correctly read a file, checking a
    couple values.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_config')
    parser = config.read_conf_file('mock_config.conf', conf_dir)
    assert parser['test-section']['test key str'] == 'test-val-str'
    assert parser.getint('test-section', 'test key int') == 123

    monkeypatch.setattr(dirs, 'get_conf_path', mock_get_conf_path)
    parser = config.read_conf_file('mock_config.conf')
    assert parser['test-section']['test key str'] == 'test-val-str'
    assert parser.getint('test-section', 'test key int') == 123



def test_cast_var():
    """
    Tests `cast_var()` for all `CastType`, so by extention tests that enum also.
    """
    good_int_str = '5'
    good_float_str = '3.14'
    good_str = 'test str'
    good_int = int(good_int_str)
    good_float = float(good_float_str)
    bad_int_str = 'five'
    bad_float_str = 'pi'

    assert good_int == config.cast_var(good_int_str, config.CastType.INT)
    assert good_float == config.cast_var(good_float_str, config.CastType.FLOAT)
    assert good_str == config.cast_var(good_str, config.CastType.STRING)

    with pytest.raises(TypeError) as ex:
        config.cast_var(good_int, 'invalid_cast_type')
    assert 'Cast failed -- unsupported type.' in str(ex.value)

    with pytest.raises(ValueError) as ex:
        config.cast_var(bad_int_str, config.CastType.INT)
    assert "invalid literal for int() with base 10: 'five'" in str(ex.value)

    with pytest.raises(ValueError) as ex:
        config.cast_var(bad_float_str, config.CastType.FLOAT)
    assert "could not convert string to float: 'pi'" in str(ex.value)

    # Skipping failed string cast due to expected rarity

    assert bad_int_str == config.cast_var(bad_int_str, config.CastType.INT,
            True)



def test_parse_list_from_conf_string():
    """
    Tests `parse_list_from_conf_string()`.
    """
    conf_list_strs = ['one', 'two', 'three']
    conf_str_simple = 'one, two, three'
    conf_str_newlines = 'one\ntwo  \r\n\r\n  three'
    conf_str_newlines_and_commas = 'one,\r\ntwo,  \r\n\r\n  three'
    conf_str_quotes = 'one, "two", \'three\''
    conf_str_delim = 'one | two | three'
    delim_char = '|'

    conf_list_ints = [1, 2, 3]
    conf_str_ints = '1, 2, 3'
    conf_str_ints_mixed = '1, 1.5, 2, two-and-a-third, 3'
    conf_list_floats = [1.0, 2.00, 3.000]
    conf_str_floats = '1.0, 2.00, 3.000'

    assert [] == config.parse_list_from_conf_string('', config.CastType.STRING)
    assert conf_list_strs == config.parse_list_from_conf_string(
            conf_str_simple, config.CastType.STRING)
    assert conf_list_strs == config.parse_list_from_conf_string(
            conf_str_newlines_and_commas, config.CastType.STRING)
    assert conf_list_strs == config.parse_list_from_conf_string(
            conf_str_newlines_and_commas, config.CastType.STRING,
            delim_newlines=True)
    assert conf_list_strs == config.parse_list_from_conf_string(
            conf_str_newlines, config.CastType.STRING,
            delim_newlines=True)
    assert conf_list_strs == config.parse_list_from_conf_string(
            conf_str_newlines, config.CastType.STRING, delim=None,
            delim_newlines=True)
    assert conf_list_strs != config.parse_list_from_conf_string(
            conf_str_quotes, config.CastType.STRING)
    assert conf_list_strs == config.parse_list_from_conf_string(
            conf_str_quotes, config.CastType.STRING, strip_quotes=True)
    assert conf_list_strs == config.parse_list_from_conf_string(
            conf_str_delim, config.CastType.STRING, delim_char)

    assert conf_list_ints == config.parse_list_from_conf_string(
            conf_str_ints, config.CastType.INT)
    assert conf_list_ints == config.parse_list_from_conf_string(
            conf_str_ints_mixed, config.CastType.INT)
    assert conf_list_floats == config.parse_list_from_conf_string(
            conf_str_floats, config.CastType.FLOAT)



def test_level_filter(caplog, capsys):
    """
    Tests `LevelFilter` entirely.

    Note that caplog does NOT respect filters added to handlers, so results in
    records/record_tuples must then also be checked against capsys to confirm
    logging actually went through or did not as expected (stderr used for all as
    default).
    """
    filter_above_info = config.LevelFilter(min_exc_level=logging.INFO)
    filter_above_info_upto_warning = config.LevelFilter('info', 30)
    filter_upto_warning = config.LevelFilter(max_inc_level='WARNING')

    handlers = {}
    loggers = {}
    test_levels = ['INFO', 'WARNING', 'ERROR']
    for level in test_levels:
        handlers[level] = logging.StreamHandler()
        handlers[level].setLevel(level)

        loggers[level] = logging.getLogger(f'test logger {level.lower()}')
        loggers[level].addHandler(handlers[level])
        loggers[level].setLevel(level)

    caplog.set_level(logging.DEBUG)

    caplog.clear()
    for level in test_levels:
        loggers[level].info(f'1. test, msg info, log {level}')
    assert caplog.record_tuples == [
        ('test logger info', logging.INFO, '1. test, msg info, log INFO'),
    ]
    assert '1. test, msg info, log INFO' in capsys.readouterr().err

    caplog.clear()
    for level in test_levels:
        loggers[level].warning(f'2. test, msg warning, log {level}')
    assert caplog.record_tuples == [
        ('test logger info', logging.WARNING,
            '2. test, msg warning, log INFO'),
        ('test logger warning', logging.WARNING,
            '2. test, msg warning, log WARNING'),
    ]
    stderr = capsys.readouterr().err
    assert '2. test, msg warning, log INFO' in stderr
    assert '2. test, msg warning, log WARNING' in stderr

    caplog.clear()
    handlers['INFO'].addFilter(filter_above_info)
    for level in test_levels:
        loggers[level].info(f'3. test, msg info, log {level}')
        loggers[level].warning(f'3. test, msg warning, log {level}')
    assert caplog.record_tuples == [
        ('test logger info', logging.INFO,
            '3. test, msg info, log INFO'),
        ('test logger info', logging.WARNING,
            '3. test, msg warning, log INFO'),
        ('test logger warning', logging.WARNING,
            '3. test, msg warning, log WARNING'),
    ]
    stderr = capsys.readouterr().err
    assert '3. test, msg info, log INFO' not in stderr
    assert '3. test, msg warning, log INFO' in stderr
    assert '3. test, msg warning, log WARNING' in stderr

    handlers['INFO'].removeFilter(filter_above_info)
    caplog.clear()
    handlers['INFO'].addFilter(filter_above_info_upto_warning)
    handlers['WARNING'].addFilter(filter_upto_warning)
    for level in test_levels:
        loggers[level].info(f'4. test, msg info, log {level}')
        loggers[level].warning(f'4. test, msg warning, log {level}')
        loggers[level].error(f'4. test, msg error, log {level}')
    assert caplog.record_tuples == [
        ('test logger info', logging.INFO,
            '4. test, msg info, log INFO'),
        ('test logger info', logging.WARNING,
            '4. test, msg warning, log INFO'),
        ('test logger info', logging.ERROR,
            '4. test, msg error, log INFO'),
        ('test logger warning', logging.WARNING,
            '4. test, msg warning, log WARNING'),
        ('test logger warning', logging.ERROR,
            '4. test, msg error, log WARNING'),
        ('test logger error', logging.ERROR,
            '4. test, msg error, log ERROR'),
    ]
    stderr = capsys.readouterr().err
    assert '4. test, msg info, log INFO' not in stderr
    assert '4. test, msg warning, log INFO' in stderr
    assert '4. test, msg error, log INFO' not in stderr
    assert '4. test, msg warning, log WARNING' in stderr
    assert '4. test, msg error, log WARNING' not in stderr
    assert '4. test, msg error, log ERROR' in stderr
