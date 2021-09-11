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
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import configparser
from enum import Enum
import itertools
import os.path

from asana_extensions.general import dirs



def read_conf_file_fake_header(conf_rel_file,
        conf_base_dir=dirs.get_conf_path(), fake_section='fake',):
    """
    Read config file in configparser format, but insert a fake header for
    first section.  This is aimed at files that are close to configparser
    format, but do not have a section header for the first section.

    The fake section name is not important.

    Args:
      conf_rel_file (str): Relative file path to config file.
      conf_base_dir (str): Base file path to use with relative path.  If not
        provided, this will use the absolute path of this module.
      fake_section (str): Fake section name, if needed.

    Returns:
      parser (ConfigParser): ConfigParser for file loaded.
    """
    conf_file = os.path.join(conf_base_dir, conf_rel_file)

    parser = configparser.ConfigParser()
    with open(conf_file, encoding="utf_8") as file:
        parser.read_file(itertools.chain(['[' + fake_section + ']'], file))

    return parser



def read_conf_file(conf_rel_file, conf_base_dir=dirs.get_conf_path()):
    """
    Read config file in configparser format.

    Args:
      conf_rel_file (str): Relative file path to config file.
      conf_base_dir (str): Base file path to use with relative path.  If not
        provided, this will use the absolute path of this module.

    Returns:
      parser (ConfigParser): ConfigParser for file loaded.
    """
    conf_file = os.path.join(conf_base_dir, conf_rel_file)

    parser = configparser.ConfigParser()
    parser.read(conf_file)

    return parser



class CastType(Enum):
    """
    Enum of cast types.

    These are used to specify a target type when casting in `castVar()`.
    """
    INT = 'int'
    FLOAT = 'float'
    STRING = 'string'



def cast_var(var, cast_type, fallback_to_original=False):
    """
    Cast variable to the specified type.

    Args:
      var (*): Variable of an unknown type.
      cast_type (CastType): Type that var should be cast to, if possible.
      fallback_to_original (bool): If true, will return original var if cast
        fails; otherwise, failed cast will raise exception.

    Returns:
      var (CastType, or ?): Same as var provided, but of the type specified by
        CastType; but if cast failed and fallback to original was true, will
        return original var in original type.

    Raises:
      (TypeError): Cannot cast because type specified is not supported.
      (ValueError): Cast failed and fallback to original was not True.
    """
    try:
        if cast_type == CastType.INT:
            return int(var)
        if cast_type == CastType.FLOAT:
            return float(var)
        if cast_type == CastType.STRING:
            return str(var)
        raise TypeError('Cast failed -- unsupported type.')

    except (TypeError, ValueError):
        if fallback_to_original:
            return var
        raise



def parse_list_from_conf_string(conf_str, val_type, delim=',',
        strip_quotes=False):
    """
    Parse a string into a list of items based on the provided specifications.

    Args:
      conf_str (str): The string to be split.
      val_type (CastType): The type to cast each element to.
      delim (str): The delimiter on which to split conf_str.
      strip_quotes (bool): Whether or not there are quotes to be stripped from
        each item after split and strip.

    Returns:
      list_out (list of val_type): List of all elements found in conf_str after
        splitting on delim.  Each element will be of val_type.  This will
        silently skip any element that cannot be cast.
    """
    if not conf_str:
        return []
    val_raw_list = conf_str.split(delim)

    list_out = []
    for val in val_raw_list:
        try:
            if strip_quotes:
                val = val.strip().strip('\'"')
            cast_val = cast_var(val.strip(), val_type)
            list_out.append(cast_val)
        except (ValueError, TypeError):
            # may have been a blank line without a delim
            pass

    return list_out
