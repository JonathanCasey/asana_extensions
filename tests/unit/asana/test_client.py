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
import warnings

import asana
import pytest

from asana_extensions.asana import client as aclient
from asana_extensions.general import config
from tests.exceptions import *                 # pylint: disable=wildcard-import
from tests.unit.asana import tester_data



@pytest.fixture(name='raise_asana_error')
def fixture_raise_asana_error(request):
    """
    Returns a function that can be used to mock a call, simply forcing it to
    raise a marked `AsanaError` sub-error.  If no marker, will use a default
    exception type.
    """
    marker = request.node.get_closest_marker('asana_error_data')
    if marker is None:
        exception_type = asana.error.InvalidRequestError # Arbitrary
    else:
        exception_type = marker.args[0]

    def mock_raise(*args, **kwargs):
        """
        Simply raise the desired error.
        """
        raise exception_type

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



@pytest.fixture(name='sections_in_project_test', scope='session')
def fixture_sections_in_project_test(project_test):
    """
    Creates some test sections in the test project and returns a list of them,
    each of which is the dict of data that should match the `data` element
    returned by the API.

    Will delete the sections once done with all tests.

    This is not being used with the autouse keyword so that, if running tests
    that do not require this section fixture, they can run more optimally
    without the need to needlessly create and delete this section.  (Also,
    could not figure out how to get rid of all syntax and pylint errors).

    ** Consumes 5 API calls. **
    (API call count is 2*num_sects + 1)
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    num_sects = 2
    client = aclient._get_client()
    me_data = aclient._get_me()

    sect_data_list = []
    for _ in range(num_sects):
        sect_name = tester_data._SECTION_TEMPLATE.substitute(
                {'sid': uuid.uuid4()})
        params = {
            'name': sect_name,
            'owner': me_data['gid'],
        }
        sect_data = client.sections.create_section_for_project(
                project_test['gid'], params)
        sect_data_list.append(sect_data)

    yield sect_data_list

    for sect_data in sect_data_list:
        client.sections.delete_section(sect_data['gid'])



@pytest.fixture(name='tasks_in_project_and_utl_test', scope='session')
def fixture_tasks_in_project_and_utl_test(project_test,
        sections_in_project_test, sections_in_utl_test):
    """
    Creates some tasks in both the user task list (in the test workspace) and
    the test project, and returns a list of them, each of which is the dict of
    data that should match the `data` element returned by the API.  The tasks
    in the user task list and the test project are the same tasks.

    This differs from the `fixture_tasks_movable_in_project_and_utl_test()` in
    that these are expected to not be altered.

    Will delete the tasks once done with all tests.

    This is not being used with the autouse keyword so that, if running tests
    that do not require this section fixture, they can run more optimally
    without the need to needlessly create and delete this section.  (Also,
    could not figure out how to get rid of all syntax and pylint errors).

    ** Consumes 7 API calls. **
    (API call count is 3*num_sects + 1)
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    num_tasks = 2
    client = aclient._get_client()
    me_data = aclient._get_me()

    task_data_list = []
    for _ in range(num_tasks):
        task_name = tester_data._TASK_TEMPLATE.substitute({'tid': uuid.uuid4()})
        params = {
            'assignee': me_data['gid'],
            'assignee_section': sections_in_utl_test[0]['gid'],
            'name': task_name,
            'projects': [
                project_test['gid'],
            ],
        }
        task_data = client.tasks.create_task(params)
        task_data_list.append(task_data)

        # No way to add project section at task creation, so need separate call
        params = {
            'task': task_data['gid'],
        }
        client.sections.add_task_for_section(sections_in_project_test[0]['gid'],
                params)

    yield task_data_list

    for task_data in task_data_list:
        client.tasks.delete_task(task_data['gid'])



@pytest.fixture(name='tasks_movable_in_project_and_utl_test', scope='session')
def fixture_tasks_movable_in_project_and_utl_test(project_test,
        sections_in_project_test, sections_in_utl_test):
    """
    Creates some tasks in both the user task list (in the test workspace) and
    the test project, and returns a list of them, each of which is the dict of
    data that should match the `data` element returned by the API.  The tasks
    in the user task list and the test project are the same tasks.

    This differs from the `fixture_tasks_in_project_and_utl_test()` in that
    these are expected to be movable.  As such, this should only be used by
    tests that factor in this moving.  If multiple test functions use this
    fixture, some sort of ordering of dependency it likely required.

    Will delete the tasks once done with all tests.

    This is not being used with the autouse keyword so that, if running tests
    that do not require this section fixture, they can run more optimally
    without the need to needlessly create and delete this section.  (Also,
    could not figure out how to get rid of all syntax and pylint errors).

    ** Consumes 7 API calls. **
    (API call count is 3*num_sects + 1)
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    num_tasks = 3
    client = aclient._get_client()
    me_data = aclient._get_me()

    task_data_list = []
    for i_task in range(num_tasks):
        task_name = tester_data._TASK_TEMPLATE.substitute({'tid': uuid.uuid4()})
        i_sect = 0
        if i_task >= 2:
            i_sect = 1
        params = {
            'assignee': me_data['gid'],
            'assignee_section': sections_in_utl_test[i_sect]['gid'],
            'name': task_name,
            'projects': [
                project_test['gid'],
            ],
        }
        task_data = client.tasks.create_task(params)
        task_data_list.append(task_data)

        # No way to add project section at task creation, so need separate call
        params = {
            'task': task_data['gid'],
        }
        client.sections.add_task_for_section(
                sections_in_project_test[i_sect]['gid'], params)

    yield task_data_list

    for task_data in task_data_list:
        client.tasks.delete_task(task_data['gid'])



def filter_result_for_test(found_data, allowed_data, match_key,
        key_by_index=False):
    """
    The asana API often returns iterators of results.  In this test module, many
    results are first filtered by the allowable values so that any additional
    items that may have been added by other tests do not conflate test results.

    This only works for single-depth `match_key`s, so, for example, it can check
    the 'gid' key if task data is supplied, but it couldn't check the 'gid' of
    the first project in the list of projects in that task data.

    Args:
      found_data ([{str:any}]): The list of data returned by the asana API for
        a query.  This is likely really a single-iteration generator, but either
        will be compatible.
      allowed_data ([{str:any}]): The list of data that is "allowed" to be in
        the `found_data`.  All other data in `found_data` will be excluded.
      match_key (str/int): The key to match in each item of the `found_data` and
        `allowed_data`.  Probably should be a string, but no reason it couldn't
        be an int if you know what you are doing.
      key_by_index (bool): Whether the results should be a dict keyed by the
        index of the allowed data item (True) or whether a simple ordered list
        should be returned (False).

    Returns:
      filt_data ([{str:any}]/{int:{str:any}}): The `found_data` that was present
        in the `allowed_data`.  This will be a dict indexed by the corresponding
        index number of the matching `allowed_data` entry if `key_by_index` is
        True; otherwise will be a list in the order of the `found_data` (which
        would be the order provided by the API if this is directly from an
        asana API query).
    """
    if key_by_index:
        filt_data = {}
    else:
        filt_data = []
    # Nested fors must be in this order - expect found_data is a single-iter gen
    for found_item in found_data:
        for i_allowed_item, allowed_item in enumerate(allowed_data):
            if found_item[match_key] == allowed_item[match_key]:
                if key_by_index:
                    filt_data[i_allowed_item] = found_item
                else:
                    filt_data.append(found_item)
                break
    return filt_data



def subtest_asana_error_handler_func(caplog, exception_type, log_index, func,
        *args, **kwargs):
    """
    Executes a subtest to confirm `@asana_error_handler` is properly decorating
    the given function.  This allows test for the given functions to setup
    anything function-specific required prior to running these same tests steps.

    Expected to be called by every function that uses the `@asana_error_handler`
    decorator.

    Args:
      caplog (Caplog): The caplog fixture from the pytest test.
      exception_type (AsanaError): The exact exception type that is expected to
        be caught.  Can be as generic as `AsanaError`, but testing for something
        more specific is better to improve coverage.
      log_index (int): The index to check in caplog for the desired exception
        log message.
      func (function): The reference to the function to call to test.
      *args ([any]): The positional arguments to pass to the function to test
        `func`.
      **kwargs ({str:any}): The keyword arguments to pass to teh function to
        test `func`.
    """
    caplog.clear()
    with pytest.raises(exception_type):
        func(*args, **kwargs)
    assert caplog.record_tuples[log_index][0] == 'asana_extensions.asana.client'
    assert caplog.record_tuples[log_index][1] == logging.ERROR
    assert 'API query failed' in caplog.messages[log_index]



@pytest.mark.no_warnings_only
def test_logging_capture_warnings(caplog):
    """
    This tests that the `logging.captureWarnings(True)` line has been executed
    in the `aclient` module.

    This must be run with the `-p no:warnings` option provided to `pytest`.  As
    a result, it is skipped by default.  See `/conftest.py` for options.
    """
    caplog.set_level(logging.WARNING)
    caplog.clear()
    warnings.warn('Test warning')
    assert caplog.record_tuples[0][0] == 'py.warnings'
    assert caplog.record_tuples[0][1] == logging.WARNING
    assert 'Test warning' in caplog.record_tuples[0][2]



def test_asana_error_handler(caplog):
    """
    Tests the `@asana_error_handler` decorator.
    """
    caplog.set_level(logging.ERROR)

    def gen_text(text1, text2, text3):
        return f'{text1} | {text2} | {text3}'

    dec_gen_text = aclient.asana_error_handler(gen_text)
    assert dec_gen_text('one', text3='three', text2='two') \
            == 'one | two | three'
    assert dec_gen_text._is_wrapped_by_asana_error_handler is True

    def raise_error(exception_type):
        raise exception_type

    dec_raise_error = aclient.asana_error_handler(raise_error)
    exception_types = [
        asana.error.PremiumOnlyError,
        asana.error.RateLimitEnforcedError,
    ]
    for exception_type in exception_types:
        subtest_asana_error_handler_func(caplog, exception_type, 0,
                dec_raise_error, exception_type)

    assert dec_raise_error._is_wrapped_by_asana_error_handler is True



@pytest.mark.parametrize('func_name', [
    '_get_me',
    'get_workspace_gid_from_name',
    'get_project_gid_from_name',
    'get_section_gid_from_name',
    'get_user_task_list_gid',
    'get_section_gids_in_project_or_utl',
    'get_tasks',
    'move_task_to_section',
])
def test_dec_usage_asana_error_handler(func_name):
    """
    Tests that functions that are expected to use the `@asana_error_handler`
    decorator do in fact have it.
    """
    func = getattr(aclient, func_name)
    assert func._is_wrapped_by_asana_error_handler is True



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

    # Function-specific practical test of @asana_error_handler
    monkeypatch.delattr(aclient._get_client, 'client')
    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file)
    subtest_asana_error_handler_func(caplog, asana.error.NoAuthorizationError,
            0, aclient._get_me)



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



@pytest.mark.asana_error_data.with_args(asana.error.ForbiddenError)
def test_get_workspace_gid_from_name(monkeypatch, caplog, raise_asana_error):
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

    # Function-specific practical test of @asana_error_handler
    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.workspaces, 'get_workspaces', raise_asana_error)
    subtest_asana_error_handler_func(caplog, asana.error.ForbiddenError, 0,
            aclient.get_workspace_gid_from_name, 'one and only')



@pytest.mark.asana_error_data.with_args(asana.error.NotFoundError)
def test_get_project_gid_from_name(monkeypatch, caplog, project_test,
        raise_asana_error):
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

    # Function-specific practical test of @asana_error_handler
    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.projects, 'get_projects', raise_asana_error)
    subtest_asana_error_handler_func(caplog, asana.error.NotFoundError, 0,
            aclient.get_project_gid_from_name, ws_gid, project_test['name'])



@pytest.mark.asana_error_data.with_args(asana.error.InvalidTokenError)
def test_get_section_gid_from_name(monkeypatch, caplog, project_test,
        sections_in_project_test, raise_asana_error):
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

    # Only need 1 section
    section_in_project_test = sections_in_project_test[0]

    # Sanity check that this works with an actual section
    try:
        sect_gid = aclient.get_section_gid_from_name(project_test['gid'],
                section_in_project_test['name'], section_in_project_test['gid'])
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    assert sect_gid == section_in_project_test['gid']

    # To ensure compatible with _extract_gid_from_name(), validate data format
    client = aclient._get_client()
    sections = client.sections.get_sections_for_project(project_test['gid'])
    section = next(sections)
    assert 'gid' in section
    assert 'name' in section
    assert 'resource_type' in section

    # Function-specific practical test of @asana_error_handler
    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.sections, 'get_sections_for_project',
            raise_asana_error)
    subtest_asana_error_handler_func(caplog, asana.error.InvalidTokenError, 0,
            aclient.get_section_gid_from_name, project_test['gid'],
            section_in_project_test['name'])



@pytest.mark.asana_error_data.with_args(asana.error.ServerError)
def test_get_user_task_list_gid(monkeypatch, caplog, raise_asana_error):
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

    # Function-specific practical test of @asana_error_handler
    client = aclient._get_client()
    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.user_task_lists, 'get_user_task_list_for_user',
            raise_asana_error)
    subtest_asana_error_handler_func(caplog, asana.error.ServerError, 0,
            aclient.get_user_task_list_gid, 0, True)



@pytest.mark.asana_error_data.with_args(asana.error.InvalidRequestError)
def test_get_section_gids_in_project_or_utl(monkeypatch, caplog, project_test,
        sections_in_project_test, raise_asana_error):
    """
    Tests the `get_section_gids_in_project_or_utl()` method.

    This does require the asana account be configured to support unit testing.
    See CONTRIBUTING.md.

    ** Consumes at least 1 API call. **
    (varies depending on data size, but only 1 call intended)

    Raises:
      (TesterNotInitializedError): If test workspace does not exist on asana
        account tied to access token, will stop test.  User must create
        manually per docs.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    caplog.set_level(logging.ERROR)

    # Only need 1 section
    section_in_project_test = sections_in_project_test[0]

    try:
        sect_gids = aclient.get_section_gids_in_project_or_utl(
                project_test['gid'])
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    assert int(section_in_project_test['gid']) in sect_gids

    # Function-specific practical test of @asana_error_handler
    client = aclient._get_client()
    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.sections, 'get_sections_for_project',
            raise_asana_error)
    subtest_asana_error_handler_func(caplog, asana.error.InvalidRequestError, 0,
            aclient.get_section_gids_in_project_or_utl, project_test['gid'])



@pytest.mark.asana_error_data.with_args(asana.error.NoAuthorizationError)
def test_get_tasks(monkeypatch, caplog,        # pylint: disable=too-many-locals
        project_test, sections_in_project_test, sections_in_utl_test,
        tasks_in_project_and_utl_test, raise_asana_error):
    """
    Tests the `get_tasks()` method.

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
        me_data = aclient._get_me()
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    ws_gid = aclient.get_workspace_gid_from_name(tester_data._WORKSPACE)

    params = {
        'assignee': me_data['gid'],
        'workspace': ws_gid,
    }
    fields = [
        'assignee_section',
        'due_at',
        'name',
        'projects',
    ]
    tasks_found = aclient.get_tasks(params, fields)
    tasks_to_check = filter_result_for_test(tasks_found,
            tasks_in_project_and_utl_test, 'gid', True)
    assert len(tasks_to_check) == len(tasks_in_project_and_utl_test)
    for i_task_expected, task_found in tasks_to_check.items():
        task_expected = tasks_in_project_and_utl_test[i_task_expected]
        assert task_found['assignee_section']['gid'] \
                    == sections_in_utl_test[0]['gid']
        assert task_found['due_at'] is None
        assert task_found['name'] == task_expected['name']
        assert task_found['projects'][0]['gid'] == project_test['gid']

    params = {
        'project': project_test['gid'],
    }
    fields = [
        'due_on',
        'memberships.section',
        'name',
        'projects',
    ]
    tasks_found = aclient.get_tasks(params, fields)
    tasks_to_check = filter_result_for_test(tasks_found,
            tasks_in_project_and_utl_test, 'gid', True)
    assert len(tasks_to_check) == len(tasks_in_project_and_utl_test)
    for i_task_expected, task_found in tasks_to_check.items():
        task_expected = tasks_in_project_and_utl_test[i_task_expected]
        assert task_found['due_on'] is None
        assert task_found['name'] == task_expected['name']
        assert task_found['projects'][0]['gid'] == project_test['gid']
        assert sections_in_project_test[0]['gid'] in \
                [m['section']['gid'] for m in task_found['memberships'] \
                    if 'section' in m]

    # Function-specific practical test of @asana_error_handler
    client = aclient._get_client()
    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.tasks, 'get_tasks', raise_asana_error)
    subtest_asana_error_handler_func(caplog, asana.error.NoAuthorizationError,
            0, aclient.get_tasks, {})



@pytest.mark.asana_error_data.with_args(asana.error.PremiumOnlyError)
def test_move_task_to_section__common(monkeypatch, caplog, raise_asana_error):
    """
    Tests common elements for the `move_task_to_section()` method.

    This does require the asana account be configured to support unit testing.
    See CONTRIBUTING.md.

    ** Consumes at least 1 API call. **
    (varies depending on data size, but only 1 call intended)

    Raises:
      (TesterNotInitializedError): If test workspace does not exist on asana
        account tied to access token, will stop test.  User must create
        manually per docs.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    caplog.set_level(logging.ERROR)

    try:
        # Simple test that project is configured, but non-error result not used
        aclient._get_me()
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    # Function-specific practical test of @asana_error_handler
    client = aclient._get_client()
    # Need to monkeypatch cached client since class dynamically creates attrs
    monkeypatch.setattr(client.sections, 'add_task_for_section',
            raise_asana_error)
    subtest_asana_error_handler_func(caplog, asana.error.PremiumOnlyError,
            0, aclient.move_task_to_section, -1, -2)



@pytest.mark.parametrize('is_utl_test, i_sect, move_to_bottom', [
    # The order is crucial, as each depends on the residual state of the tasks
    (False, 1, False),
    (False, 0, True),
    (True,  1, False),
    (True,  0, True),
])
def test_move_task_to_section__parametrized(is_utl_test, i_sect, move_to_bottom,
        sections_in_project_test, sections_in_utl_test,
        tasks_movable_in_project_and_utl_test):
    """
    Tests parametrized paths for the `move_task_to_section()` method.

    This does require the asana account be configured to support unit testing.
    See CONTRIBUTING.md.

    ** Consumes at least 14 API calls total. **
    (varies depending on data size, but only 4 calls intended)
    (API call count is 3 [+1 if not is_utl_test] for each parameter)
    (  with equal num with and without is_utl_test: 3.5*num_parameters)

    Raises:
      (TesterNotInitializedError): If test workspace does not exist on asana
        account tied to access token, will stop test.  User must create
        manually per docs.
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    try:
        # Simple test that project is configured, but non-error result not used
        aclient._get_me()
    except aclient.DataNotFoundError as ex:
        # This is an error with the tester, not the module under test
        raise TesterNotInitializedError('Cannot run unit tests: Must create a'
                + f' workspace named "{tester_data._WORKSPACE}" in the asana'
                + ' account tied to access token in .secrets.conf') from ex

    if is_utl_test:
        sects = sections_in_utl_test
    else:
        sects = sections_in_project_test

    aclient.move_task_to_section(
            tasks_movable_in_project_and_utl_test[0]['gid'],
            sects[i_sect]['gid'], move_to_bottom)
    params = {
        'section': sects[i_sect]['gid'],
    }
    tasks_found = aclient.get_tasks(params)
    tasks_to_check = filter_result_for_test(tasks_found,
            tasks_movable_in_project_and_utl_test, 'gid')
    assert len(tasks_to_check) == 2
    if move_to_bottom:
        assert tasks_to_check[-1]['gid'] \
                == tasks_movable_in_project_and_utl_test[0]['gid']
    else:
        assert tasks_to_check[0]['gid'] \
                == tasks_movable_in_project_and_utl_test[0]['gid']



def test_pagination(project_test, sections_in_project_test):
    """
    Tests compatibility with `asana` package to ensure that any pagination is
    handled in a way that is compatible with how this project expects it.

    ** Consumes at least 2 API calls. **
    (varies depending on data size, but only 2 calls intended)
    """
    client = aclient._get_client()
    client.options['page_size'] = 1

    sect_gids = aclient.get_section_gids_in_project_or_utl(project_test['gid'])

    # Should match exactly, but other tests may have added more sects to server
    assert len(sect_gids) >= len(sections_in_project_test)
    for sect in sections_in_project_test:
        assert int(sect['gid']) in sect_gids
