# -*- coding: utf-8 -*-
"""ASC-240: Verify the requested glance images were uploaded

RPC 10+ manual test 10
"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest
import pytest_rpc.helpers as helpers
from conftest import expect_os_property


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('912080b8-0467-11e9-933a-0025227c8120')
@pytest.mark.jira('ASC-1314')
def test_snapshot_instance(os_api_conn,
                           create_server,
                           tiny_cirros_server,
                           openstack_properties):
    """Verify that a server can be created from a snapshot image.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        create_server (def): A factory function for generating servers.
        tiny_cirros_server (openstack.compute.v2.server.Server): Create a
            'm1.tiny' server instance with a Cirros image.
        openstack_properties(dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    # Create snapshot image from server .
    snapshot_image = os_api_conn.create_image_snapshot(
        wait=True,
        name="snapshot_image_of_{}".format(tiny_cirros_server.name),
        server=tiny_cirros_server
    )

    # Validate that image was created successfully.
    assert expect_os_property(retries=10,
                              os_object=snapshot_image,
                              os_service='image',
                              os_api_conn=os_api_conn,
                              os_prop_name='status',
                              expected_value='active')

    # Create server from snapshot. (Automatically validated by fixture)
    snapshot_server = create_server(
        name="snapshot_server_{}".format(helpers.generate_random_string()),
        image=snapshot_image,
        flavor=openstack_properties['tiny_flavor'],
        network=openstack_properties['test_network'],
        key_name=openstack_properties['key_name'],
        security_groups=[openstack_properties['security_group']]
    )

    # Validate server was created from the snapshot image.
    assert snapshot_server.image.id == snapshot_image.id
