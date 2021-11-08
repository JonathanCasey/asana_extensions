#!/usr/bin/env python3
"""
Configures pytest as needed.  This file normally does not need to exist, but is
used here to share and configure items for the /tests/unit/asana subpackage.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
# pylint: disable=protected-access # Allow for purpose of testing those elements

import uuid

import pytest

from asana_extensions.asana import client as aclient
from tests.unit.asana import tester_data



@pytest.fixture(name='sections_in_utl_test', scope='session')
def fixture_sections_in_utl_test():
    """
    Creates some test sections in the user task list (in the test workspace) and
    returns a list of them, each of which is the dict of data that should match
    the `data` element returned by the API.

    Will delete the sections once done with all tests.

    This is not being used with the autouse keyword so that, if running tests
    that do not require this section fixture, they can run more optimally
    without the need to needlessly create and delete this section.  (Also,
    could not figure out how to get rid of all syntax and pylint errors).

    ** Consumes at least 7 API calls. **
    (API call count is 2*num_sects + at least 3)
    (varies depending on data size, but only 7 calls intended)
    """
    # pylint: disable=no-member     # asana.Client dynamically adds attrs
    num_sects = 2
    client = aclient._get_client()
    me_data = aclient._get_me()
    ws_gid = aclient.get_workspace_gid_from_name(tester_data._WORKSPACE)
    utl_gid = str(aclient.get_user_task_list_gid(ws_gid, is_me=True))

    sect_data_list = []
    for _ in range(num_sects):
        sect_name = tester_data._SECTION_TEMPLATE.substitute(
                {'sid': uuid.uuid4()})
        params = {
            'name': sect_name,
            'owner': me_data['gid'],
        }
        sect_data = client.sections.create_section_for_project(utl_gid, params)
        sect_data_list.append(sect_data)

    yield sect_data_list

    for sect_data in sect_data_list:
        client.sections.delete_section(sect_data['gid'])
