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
import os.path

import pytest

from asana_extensions.general import config



def test_read_conf_file_fake_header():
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



def test_read_conf_file():
    """
    Tests that the `read_conf_file()` will correctly read a file, checking a
    couple values.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_config')
    parser = config.read_conf_file('mock_config.conf', conf_dir)
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
    conf_str_newlines = 'one,\r\ntwo,  \r\n\r\n  three'
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
            conf_str_newlines, config.CastType.STRING)
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
