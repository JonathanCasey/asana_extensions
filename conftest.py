#!/usr/bin/env python3
"""
Configures pytest as needed.  This file can be left completely empty but must
exist.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import pytest



def pytest_addoption(parser):
    """
    Adds additional CLI options for invoking `pytest`.

    https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_addoption

    Args:
      parser (Parser): Parser to which options and ini-file values can be added.
    """
    parser.addoption('--run-no-warnings-only',
            action='store_true',
            default=False,
            help='Run tests requiring warnings plugin disabled ONLY.',
    )



def pytest_configure(config):
    """
    Performs initial configuration after CLI options have been parsed.

    https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_configure

    Args:
      config (Config): Config object to which configurations can be added.  See
        pytest docs: https://docs.pytest.org/en/6.2.x/reference.html#config
    """
    config.addinivalue_line('markers',
            'no_warnings_only: Mark test as requiring warnings plugin disabled')



def pytest_collection_modifyitems(config, items):
    """
    After collection has been performed, can filter, reorder, or otherwise
    modify test items.

    https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_collection_modifyitems

    Modifications implemented:
    - `--run-no-warnings-only` provided/missing will skip tests appropriately.

    Args:
      config (Config): Config object containing the pytest configuration.  See
        pytest docs: https://docs.pytest.org/en/6.2.x/reference.html#config
      items ([Items]): The list of pytest options collected that can be
        modified.  See docs:
        https://docs.pytest.org/en/6.2.x/reference.html#pytest.Item .  The Node
        docs from which it inherits are also very helpful:
        https://docs.pytest.org/en/6.2.x/reference.html#node
    """
    if config.getoption('--run-no-warnings-only'):
        skip_non_no_warnings_only = pytest.mark.skip(
                reason='Must omit --run-no-warnings-only option to run')
        for item in items:
            if 'no_warnings_only' not in item.keywords:
                item.add_marker(skip_non_no_warnings_only)
    else:
        skip_no_warnings_only = pytest.mark.skip(
                reason='Need --run-no-warnings-only option to run')
        for item in items:
            if 'no_warnings_only' in item.keywords:
                item.add_marker(skip_no_warnings_only)
