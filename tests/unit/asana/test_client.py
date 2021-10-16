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
import uuid

import asana
import pytest

from asana_extensions.asana import client as aclient
from asana_extensions.general import config
from tests.exceptions import *                 # pylint: disable=wildcard-import
from tests.unit.asana import tester_data



@pytest.fixture(name='raise_no_authorization_error')
def fixture_raise_no_authorization_error():
    """
    Returns a function that can be mocked over a call that simply forces it to
    raise the asana.error.NoAuthorizationError.
    """
    def mock_raise(*args, **kwargs):
        """
        Simply raise the desired error.
        """
        raise asana.error.NoAuthorizationError()

    return mock_raise



@pytest.fixture(name='raise_not_found_error')
def fixture_raise_not_found_error():
    """
    Returns a function that can be mocked over a call that simply forces it to
    raise the asana.error.NotFoundError.
    """
    def mock_raise(*args, **kwargs):
        """
        Simply raise the desired error.
        """
        raise asana.error.NotFoundError()

    return mock_raise



@pytest.fixture(name='project_test', scope='session')
def fixture_project_test():
    """
    Creates a test project and returns the dict of data that should match the
    'data' element returned by the API.

    Will delete the project once done with all tests.

    This is not being used with the autouse keyword so that, if running tests
    that do not require this project fixture, they can run more optimally
    without the need to needlessly create and delete this project.  (Also,
    could not figure out how to get rid of all syntax and pylint errors).

    ** Consumes 3 API calls. **
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    proj_name = tester_data._PROJECT_TEMPLATE.substitute({'pid': uuid.uuid4()})
    client = aclient._get_client()
    ws_gid = aclient.get_workspace_gid_from_name(tester_data._WORKSPACE)
    me_data = aclient._get_me()
    params = {
        'name': proj_name,
        'owner': me_data['gid'],
    }
    proj_data = client.projects.create_project_for_workspace(ws_gid, params)

    yield proj_data

    client.projects.delete_project(proj_data['gid'])



@pytest.fixture(name='section_test', scope='session')
def fixture_section_test(project_test):
    """
    Creates a test section and returns the dict of data that should match the
    'data' element returned by the API.

    Will delete the section once done with all tests.

    This is not being used with the autouse keyword so that, if running tests
    that do not require this section fixture, they can run more optimally
    without the need to needlessly create and delete this section.  (Also,
    could not figure out how to get rid of all syntax and pylint errors).

    ** Consumes 3 API calls. **
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    sect_name = tester_data._SECTION_TEMPLATE.substitute({'sid': uuid.uuid4()})
    client = aclient._get_client()
    me_data = aclient._get_me()
    params = {
        'name': sect_name,
        'owner': me_data['gid'],
    }
    sect_data = client.sections.create_section_for_project(project_test['gid'],
            params)

    yield sect_data

    client.sections.delete_section(sect_data['gid'])



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



def test__find_gid_from_name(caplog):
    """
    Tests the `_find_gid_from_name()` method.

    No API calls.  Methods that use this `_find_gid_from_name()` method will
    verify API compatibility then.  This stays focused on testing logic.
    """
    caplog.set_level(logging.INFO)

    data = [
        {
            'gid': 1,
            'name': 'one and only',
            'resource_type': 'workspace',
        },
        {
            'gid': 2,
            'name': 'two with dupe',
            'resource_type': 'workspace',
        },
        {
            'gid': 3,
            'name': 'two with dupe',
            'resource_type': 'workspace',
        },
        {
            'gid': 4,
            'name': 'not workspace',
            'resource_type': 'organization',
        },
    ]
    resource_type = 'workspace'

    gid = aclient._find_gid_from_name(data, resource_type, 'one and only', 1)
    assert gid == 1

    caplog.clear()
    gid = aclient._find_gid_from_name(data, resource_type, 'one and only')
    assert gid == 1
    assert caplog.record_tuples == [
            ('asana_extensions.asana.client', logging.INFO,
                'GID of workspace "one and only" is 1'),
    ]

    with pytest.raises(aclient.MismatchedDataError):
        aclient._find_gid_from_name(data, resource_type, 'one and only', -1)

    with pytest.raises(aclient.DuplicateNameError):
        aclient._find_gid_from_name(data, resource_type, 'two with dupe')

    with pytest.raises(aclient.DataNotFoundError):
        aclient._find_gid_from_name(data, resource_type, 'invalid name')



def test_get_workspace_gid_from_name(monkeypatch, caplog,
        raise_no_authorization_error):
    """
    Tests the `get_workspace_gid_from_name()` method.

    This does require the asana account be configured to support unit testing.
    See CONTRIBUTING.md.

    ** Consumes at least 2 API calls. **
    (varies depending on data size, but only 2 calls intended)

    Raises:
      (TesterNotInitializedError): If test workspace does not exist on asana
        account tied to access token, will stop test.  User must create
        manually per docs.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    caplog.set_level(logging.ERROR)

    try:
        aclient.get_workspace_gid_from_name(tester_data._WORKSPACE)
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    # To ensure compatible with _extract_gid_from_name(), validate data format
    client = aclient._get_client()
    workspaces = client.workspaces.get_workspaces()
    workspace = next(workspaces)
    assert 'gid' in workspace
    assert 'name' in workspace
    assert 'resource_type' in workspace

    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.workspaces, 'get_workspaces',
            raise_no_authorization_error)

    caplog.clear()
    with pytest.raises(asana.error.NoAuthorizationError):
        aclient.get_workspace_gid_from_name('one and only')
    assert caplog.record_tuples == [
            ('asana_extensions.asana.client', logging.ERROR,
                "Failed to access API in get_workspace_gid_from_name() - Not"
                + " Authorized: No Authorization"),
    ]



def test_get_project_gid_from_name(monkeypatch, caplog, project_test,
        raise_no_authorization_error):
    """
    Tests the `get_project_gid_from_name()` method.

    This does require the asana account be configured to support unit testing.
    See CONTRIBUTING.md.

    ** Consumes at least 3 API calls. **
    (varies depending on data size, but only 3 calls intended)

    Raises:
      (TesterNotInitializedError): If test workspace does not exist on asana
        account tied to access token, will stop test.  User must create
        manually per docs.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    caplog.set_level(logging.ERROR)

    try:
        ws_gid = aclient.get_workspace_gid_from_name(tester_data._WORKSPACE)
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    # Sanity check that this works with an actual project
    proj_gid = aclient.get_project_gid_from_name(ws_gid, project_test['name'],
            project_test['gid'])
    assert proj_gid == project_test['gid']

    # To ensure compatible with _extract_gid_from_name(), validate data format
    client = aclient._get_client()
    projects = client.projects.get_projects({'workspace': ws_gid})
    project = next(projects)
    assert 'gid' in project
    assert 'name' in project
    assert 'resource_type' in project

    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.projects, 'get_projects',
            raise_no_authorization_error)

    caplog.clear()
    with pytest.raises(asana.error.NoAuthorizationError):
        aclient.get_project_gid_from_name(ws_gid, project_test['name'])
    assert caplog.record_tuples == [
            ('asana_extensions.asana.client', logging.ERROR,
                "Failed to access API in get_project_gid_from_name() - Not"
                + " Authorized: No Authorization"),
    ]



def test_get_section_gid_from_name(monkeypatch, caplog, project_test,
        section_test, raise_no_authorization_error):
    """
    Tests the `get_section_gid_from_name()` method.

    This does require the asana account be configured to support unit testing.
    See CONTRIBUTING.md.

    ** Consumes at least 2 API calls. **
    (varies depending on data size, but only 2 calls intended)

    Raises:
      (TesterNotInitializedError): If test workspace does not exist on asana
        account tied to access token, will stop test.  User must create
        manually per docs.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    caplog.set_level(logging.ERROR)

    # Sanity check that this works with an actual project
    try:
        sect_gid = aclient.get_section_gid_from_name(project_test['gid'],
                section_test['name'], section_test['gid'])
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    assert sect_gid == section_test['gid']

    # To ensure compatible with _extract_gid_from_name(), validate data format
    client = aclient._get_client()
    sections = client.sections.get_sections_for_project(project_test['gid'])
    section = next(sections)
    assert 'gid' in section
    assert 'name' in section
    assert 'resource_type' in section

    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.sections, 'get_sections_for_project',
            raise_no_authorization_error)

    caplog.clear()
    with pytest.raises(asana.error.NoAuthorizationError):
        aclient.get_section_gid_from_name(project_test['gid'],
                section_test['name'])
    assert caplog.record_tuples == [
            ('asana_extensions.asana.client', logging.ERROR,
                "Failed to access API in get_section_gid_from_name() - Not"
                + " Authorized: No Authorization"),
    ]



def test_get_user_task_list_gid(monkeypatch, caplog,
        raise_no_authorization_error, raise_not_found_error):
    """
    Tests the `get_user_task_list_gid()` method.

    This does require the asana account be configured to support unit testing.
    See CONTRIBUTING.md.

    ** Consumes at least 4 API calls. **
    (varies depending on data size, but only 4 calls intended)

    Raises:
      (TesterNotInitializedError): If test workspace does not exist on asana
        account tied to access token, will stop test.  User must create
        manually per docs.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    caplog.set_level(logging.ERROR)

    try:
        ws_gid = aclient.get_workspace_gid_from_name(tester_data._WORKSPACE)
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    me_gid = aclient._get_me()['gid']
    me_utl_gid = aclient.get_user_task_list_gid(ws_gid, True)
    uid_utl_gid = aclient.get_user_task_list_gid(ws_gid, user_gid=me_gid)
    assert me_utl_gid == uid_utl_gid
    assert me_utl_gid > 0

    with pytest.raises(AssertionError) as ex:
        aclient.get_user_task_list_gid(0)
    assert 'Must provide `is_me` or `user_gid`, but not both.' in str(ex.value)

    with pytest.raises(AssertionError) as ex:
        aclient.get_user_task_list_gid(0, True, 0)
    assert 'Must provide `is_me` or `user_gid`, but not both.' in str(ex.value)

    client = aclient._get_client()
    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.user_task_lists, 'get_user_task_list_for_user',
            raise_no_authorization_error)
    caplog.clear()
    with pytest.raises(asana.error.NoAuthorizationError):
        aclient.get_user_task_list_gid(0, True)
    assert caplog.record_tuples == [
            ('asana_extensions.asana.client', logging.ERROR,
                "Failed to access API in get_user_task_list_gid() - Not"
                + " Authorized: No Authorization"),
    ]

    monkeypatch.setattr(client.user_task_lists, 'get_user_task_list_for_user',
            raise_not_found_error)
    caplog.clear()
    with pytest.raises(asana.error.NotFoundError):
        aclient.get_user_task_list_gid(0, True)
    assert caplog.record_tuples == [
            ('asana_extensions.asana.client', logging.ERROR,
                "Could not find requested data in get_user_task_list_gid():"
                + " Not Found"),
    ]
