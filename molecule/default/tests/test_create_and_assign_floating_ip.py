# -*- coding: utf-8 -*-
"""ASC-240: Verify the requested glance images were uploaded

RPC 10+ manual test 10
"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest
from conftest import ping_from_mnaio


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('ab24ffbd-798b-11e8-a2b2-6c96cfdb2e43')
@pytest.mark.jira('ASC-254', 'ASC-1311')
def test_assign_floating_ip_to_instance(os_api_conn,
                                        create_server,
                                        openstack_properties):
    """Verify that a floating IP can be attached to a server instance.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        create_server (def): A factory function for generating servers.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    # Delete all unattached floating IPs.
    os_api_conn.delete_unattached_floating_ips(retry=3)

    # Create server without floating IP. (Automatically validated by fixture)
    test_server = create_server(
        image=openstack_properties['cirros_image'],
        flavor=openstack_properties['tiny_flavor'],
        auto_ip=False,
        network=openstack_properties['test_network'],
        key_name=openstack_properties['key_name'],
        security_groups=[openstack_properties['security_group']]
    )

    # Create floating IP address and attach to test server.
    floating_ip = os_api_conn.create_floating_ip(
        wait=True,
        server=test_server,
        network=openstack_properties['network_name']
    )

    assert ping_from_mnaio(floating_ip.floating_ip_address, retries=5)
