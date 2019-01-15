# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import pytest
from pprint import pformat
from munch import unmunchify


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc5630-432a-11e8-b9da-6a00035510c0')
@pytest.mark.jira('asc-222')
def test_cinder_service(os_api_conn):
    """Test to verify that cinder service is enabled

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
    """

    # Getting the list of services (return list of Munch Python dictionaries)
    service_list = os_api_conn.list_services()

    filtered_services = list(filter(lambda d: d['name'].lower() == 'cinder',
                                    service_list))
    assert len(filtered_services) > 0, \
        "cinder service is not found!\n{}".format(pformat(
            unmunchify(service_list)))
    assert filtered_services[0]['enabled'], "cinder service not enabled!\n{}"\
        .format(pformat(unmunchify(service_list)))
