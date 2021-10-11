#!/usr/bin/env python3
"""
Tests the asana_extensions.asana.client functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import logging

import asana
import pytest

from asana_extensions.asana import client as aclient
from asana_extensions.general import config
from tests.exceptions import *                 # pylint: disable=wildcard-import
from tests.unit.asana import tester_data



def test__get_client(monkeypatch):
    """
    Tests the `_get_client()` method.

    This relies on /config/.secrets.conf being setup with a real personal access
    token.
    """
    client = aclient._get_client()
    assert client is not None

    def mock_read_conf_file(conf_rel_file,     # pylint: disable=unused-argument
            conf_base_dir=None):               # pylint: disable=unused-argument
        """
        Return an empty dict instead of loading from file.
        """
        return {}

    # read_conf_file() returning bad config allows to confirm client cache works
    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file)
    client = aclient._get_client()
    assert client is not None

    monkeypatch.delattr(aclient._get_client, 'client')
    with pytest.raises(aclient.ClientCreationError) as ex:
        aclient._get_client()
    assert "Could not create client - Could not find necessary section/key in" \
            + " .secrets.conf: 'asana'" in str(ex.value)



def test__get_me(monkeypatch, caplog):
    """
    Tests the `_get_me()` method.

    This relies on /config/.secrets.conf being setup with a real personal access
    token.

    ** Consumes 2 API calls. **
    """
    caplog.set_level(logging.WARNING)

    me_data = aclient._get_me()
    assert me_data['gid']

    def mock_read_conf_file(conf_rel_file,     # pylint: disable=unused-argument
            conf_base_dir=None):               # pylint: disable=unused-argument
        """
        Return a bad personal access token to pass client creation but fail API.
        """
        return {
            'asana': {
                'personal access token': 'bad pat',
            },
        }

    caplog.clear()
    monkeypatch.delattr(aclient._get_client, 'client')
    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file)
    with pytest.raises(asana.error.NoAuthorizationError):
        aclient._get_me()
    assert caplog.record_tuples == [
            ('asana_extensions.asana.client', logging.ERROR,
                "Failed to access API in _get_me() - Not Authorized:"
                + " No Authorization: Not Authorized"),
    ]



def test_get_workspace_gid_from_name():
    """
    Tests the `get_workspace_gid_from_name()` method.

    This does require the asana account be configured to support unit testing.
    See CONTRIBUTING.md.

    ** Consumes at least 1 API call. ** (varies depending on data size)

    Raises:
      (TesterNotInitializedError)
    """
    try:
        aclient.get_workspace_gid_from_name(tester_data._WORKSPACE)
    except aclient.DataNotFoundError as ex:
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex
