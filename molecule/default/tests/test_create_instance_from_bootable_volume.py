# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import pytest
from pytest_rpc.helpers import ping_from_mnaio


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('8b701dbc-7584-11e8-ba5b-fe14fb7452aa')
@pytest.mark.jira('ASC-462', 'ASC-1313')
def test_create_instance_from_bootable_volume(create_volume,
                                              create_server,
                                              openstack_properties):
    """Verify that a server can be created from a bootable volume.

    Args:
        create_volume (def): A factory function for generating volumes.
        create_server (def): A factory function for generating servers.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    # Create bootable volume.
    test_volume = create_volume(
        size=1,
        image=openstack_properties['cirros_image'],
        bootable=True
    )

    # Create server without floating IP. (Automatically validated by fixture)
    test_server = create_server(
        flavor=openstack_properties['tiny_flavor'],
        network=openstack_properties['test_network'],
        key_name=openstack_properties['key_name'],
        boot_volume=test_volume,
        security_groups=[openstack_properties['security_group']]
    )

    assert ping_from_mnaio(test_server.accessIPv4, retries=5)
