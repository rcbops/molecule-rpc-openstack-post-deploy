# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import pytest
from conftest import ping_from_mnaio


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('8b701dbc-7584-11e8-ba5b-fe14fb7452aa')
@pytest.mark.jira('ASC-462', 'ASC-1313')
def test_create_instance_from_bootable_volume(os_api_conn,
                                              create_volume,
                                              create_server,
                                              openstack_properties):
    """Test to verify that a bootable volume can be created based on a
    Glance image.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        create_server (def): A factory function for generating servers.
        create_volume (def): A factory function for generating volumes.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    # Delete all unattached floating IPs.
    os_api_conn.delete_unattached_floating_ips(retry=3)

    # Create bootable volume.
    test_volume = create_volume(
        size=1,
        image=openstack_properties['cirros_image'],
        bootable=True
    )

    # Create server without floating IP. (Automatically validated by fixture)
    test_server = create_server(
        flavor=openstack_properties['tiny_flavor'],
        auto_ip=False,
        network=openstack_properties['test_network'],
        key_name=openstack_properties['key_name'],
        boot_volume=test_volume,
        security_groups=[openstack_properties['security_group']]
    )

    # Create floating IP address and attach to test server.
    floating_ip = os_api_conn.create_floating_ip(
        wait=True,
        server=test_server,
        network=openstack_properties['network_name']
    )

    assert ping_from_mnaio(floating_ip.floating_ip_address, retries=5)
