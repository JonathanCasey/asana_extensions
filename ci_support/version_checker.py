#!/usr/bin/env python3
"""
Checks the version string to ensure it conforms to a valid format.

This uses python import, so this must be called from a proper python env where
the directories-under-test are accessible.  In other words, it is best to call
from project root as
`python3 ci_support/version_checker.py -d`.

Entire file is excluded from unit testing / code cov; but is still linted.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import argparse
import re
import sys

from asana_extensions import version



def main(dev_state):                         # pylint: disable=too-many-branches
    """
    Main entry point for this module.  Will check the version string and
    validate it based on the provided args.

    Args:
      dev_state (str): The development state to check the version string format
        against.  See the argparse argument choices for possible values.
    """
    full_ver_str = version.get_full_version_string()
    full_ver_parts = full_ver_str.split('_')
    if len(full_ver_parts) != 3:
        print('Full version invalid.  Perhaps underscores were added?')
        sys.exit(1)

    dotted_ver_parts = full_ver_parts[0].split('+')

    if not 0 < len(dotted_ver_parts) < 3:
        print('Dotted (non-timestamp, non-git) portion invalid.  Perhaps more'
                + ' than 1 plus (+) sign were added, or version is empty?')
        sys.exit(2)

    if not is_version_base_valid(dotted_ver_parts[0]):
        print('Dotted (non-timestamp, non-git) portion does not conform to'
                + ' psuedo-semver format (excluding possible dev marker).')
        sys.exit(3)

    is_dev_valid = None
    if len(full_ver_parts) == 1:
        is_dev_valid = is_version_dev_valid(dotted_ver_parts[1])

    if is_dev_valid is False:
        print('Invalid dev marker format.  Only allowed is `+dev`.')
        sys.exit(4)

    if dev_state == 'dev-disallowed':
        if is_dev_valid is None:
            print('Success: Confirmed dev marker disallowed.')
            sys.exit(0)
        if is_dev_valid is True:
            print('Failure: Dev disallowed, but dev marker present.')
            sys.exit(5)
        print('Failure: Unknown failure in check dev disallowed.')
        sys.exit(6)

    if dev_state == 'dev-required':
        if is_dev_valid is True:
            print('Success: Confirmed dev marker required.')
            sys.exit(0)
        if is_dev_valid is None:
            print('Failure: Dev required, but dev marker missing.')
            sys.exit(7)
        print('Failure: Unknown failure in check dev required.')
        sys.exit(8)

    if dev_state == 'dev-any':
        if is_dev_valid is True or is_dev_valid is None:
            print('Success: Confirmed dev marker can be present or missing.')
            sys.exit(0)
        print('Failure: Unknown failure in check dev any.')
        sys.exit(9)

    print('Failure: Unknown failure due to unexpected dev_state value.')
    sys.exit(10)



def is_version_base_valid(dotted_ver_no_dev):
    """
    Checks if the base version is a valid format.  This should be roughly
    semver per the notes in `version.py`.

    Args:
      dotted_ver_no_dev (str): The version string to check, such as `v1.2.3-4`.
        This should exclude anything after the `+` sign if applicable.

    Returns:
      (bool): True if version string is a valid format; False otherwise.
    """
    return re.match(r'^v[0-9x]+.[0-9x]+.[0-9x]+(-[0-9a-z]+)?$',
            dotted_ver_no_dev) is not None



def is_version_dev_valid(dotted_ver_dev):
    """
    Checks if the development marker is valid.

    Args:
      dotted_ver_dev (str): The dev marker portion of the version string to
        check.  This should have already stripped the plus (`+`) sign that needs
        to immediately precede it.

    Returns:
      (bool or None): True if the dev marker is present and is the correct
        format; False if there is text but it is the wrong format; None if the
        string is empty.
    """
    if not dotted_ver_dev:
        return None

    if dotted_ver_dev.lower() == 'dev':
        return True

    return False



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process inputs.')
    parser.add_argument('dev-state',
            choices=['dev-disallowed', 'dev-required', 'dev-any'],
            help='Indicate the development state of the project for checking'
                + ' if the version is appropriate.  It gives all 3 possibilies:'
                + ' disallowed, required, or does not matter.')

    main(**vars(parser.parse_args()))
