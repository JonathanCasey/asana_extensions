#!/usr/bin/env python3
"""
Tests the asana_extensions.asana.asana_client functionality.

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

from asana_extensions.asana import asana_client
from asana_extensions.general import config



@pytest.fixture(name='mock_read_conf_file_bad_pat')
def fixture_mock_read_conf_file_bad_pat():
    """
    A mock function to monkeypatch in to read a conf file with a bad personal
    access token.

    Returns:
      (method): Returns a method that will mock reading the conf file.  Intended
        to be monkeypatched in for the equivalent method in config.
    """
    def mock_read_conf_file(conf_rel_file,     # pylint: disable=unused-argument
            conf_base_dir=None):               # pylint: disable=unused-argument
        """
        """
        return {
            'asana': {
                'personal access token': 'bad pat',
            },
        }

    return mock_read_conf_file



def test__get_client(monkeypatch):
    """
    Tests the `_get_client()` method.

    This relies on /config/.secrets.conf being setup with a real personal access
    token.
    """
    client = asana_client._get_client()
    assert client is not None

    def mock_read_conf_file(conf_rel_file,     # pylint: disable=unused-argument
            conf_base_dir=None):               # pylint: disable=unused-argument
        """
        Return an empty dict instead of loading from file.
        """
        return {}

    # read_conf_file() returning bad config allows to confirm client cache works
    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file)
    client = asana_client._get_client()
    assert client is not None

    monkeypatch.delattr(asana_client._get_client, 'client')
    with pytest.raises(asana_client.ClientCreationError) as ex:
        asana_client._get_client()
    assert "Could not create client - Could not find necessary section/key in" \
            + " .secrets.conf: 'asana'" in str(ex.value)



def test__get_me(monkeypatch, caplog, mock_read_conf_file_bad_pat):
    """
    Tests the `_get_me()` method.

    This relies on /config/.secrets.conf being setup with a real personal access
    token.

    ** Consumes 2 API calls. **
    """
    caplog.set_level(logging.WARNING)

    me_data = asana_client._get_me()
    assert me_data['gid']

    monkeypatch.delattr(asana_client._get_client, 'client')
    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file_bad_pat)
    caplog.clear()
    with pytest.raises(asana.error.NoAuthorizationError):
        asana_client._get_me()
    assert caplog.record_tuples == [
            ('asana_extensions.asana.asana_client', logging.ERROR,
                "Failed to access API in _get_me() - Not Authorized:"
                + " No Authorization: Not Authorized"),
    ]
