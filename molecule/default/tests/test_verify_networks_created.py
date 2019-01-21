# -*- coding: utf-8 -*-
"""ASC-239: Verify the correct networks were created

RPC 10+ manual test 9
"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc646b-432a-11e8-b858-6a00035510c0')
@pytest.mark.jira('ASC-239', 'ASC-1332')
def test_verify_network_list(os_api_conn, openstack_properties):
    """Verify that networks were created.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    expected_networks = (openstack_properties['private_net'],
                         openstack_properties['network_name'])

    for expected_network in expected_networks:
        assert os_api_conn.get_network(expected_network)


@pytest.mark.test_id('d7fc65fa-432a-11e8-a2ae-6a00035510c0')
@pytest.mark.jira('ASC-239', 'ASC-1332')
def test_verify_subnet_list(os_api_conn, openstack_properties):
    """Verify that subnets were created.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    expected_subnets = (openstack_properties['private_network_subnet'],
                        openstack_properties['gateway_network_subnet'])

    for expected_subnet in expected_subnets:
        assert os_api_conn.get_subnet(expected_subnet)
