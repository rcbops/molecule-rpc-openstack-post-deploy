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
def test_cinder_service(os_api_conn, openstack_properties):
    """Test to verify that cinder service is enabled

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """
    # Getting the right cinder service to check:
    #    Cinder API V1 was removed in Queens release (os_version_major == 17)
    #    (https://docs.openstack.org/releasenotes/horizon/rocky.html)
    #
    #    Cinder API V2 is deprecated in Rocky (os_version_major == 18)
    #    https://developer.openstack.org/api-ref/block-storage/
    #
    #    Cinder API V3 is already in Queens and later.
    if openstack_properties['os_version_major'] < 17:
        cinder_service = 'cinder'
    else:
        cinder_service = 'cinderv3'

    # Getting the list of services (return list of Munch Python dictionaries)
    service_list = os_api_conn.list_services()

    filtered_services = list(filter(lambda d:
                                    d['name'].lower() == cinder_service,
                                    service_list))
    assert len(filtered_services) > 0, \
        "Supported cinder service '{}' not found!\n{}\n"\
        .format(cinder_service, pformat(unmunchify(service_list)))
    assert filtered_services[0]['enabled'],\
        "Supported cinder service '{}' not enabled!\n{}\n" \
        .format(cinder_service, pformat(unmunchify(service_list)))
