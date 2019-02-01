# -*- coding: utf-8 -*-
"""ASC-256: Verify Cinder volume creation.

RPC 10+ manual test 14.
"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest
from pytest_rpc.helpers import expect_os_property


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('02a17d7d-4a42-11e8-bdcf-6a00035510c0')
@pytest.mark.jira('asc-256')
def test_cinder_volume_created(os_api_conn,
                               create_volume,
                               openstack_properties):
    """Test to verify that a cinder volume can be created based on a
    Glance image.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        create_volume (def): A factory function for generating volumes.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    # Create cinder volume (non-bootable)
    test_cinder_volume = create_volume(
        size=2,
        image=openstack_properties['cirros_image'],
        bootable=False
    )

    # Validate that image was created successfully.
    assert expect_os_property(retries=3,
                              os_object=test_cinder_volume,
                              os_service='volume',
                              os_api_conn=os_api_conn,
                              os_prop_name='is_bootable',
                              expected_value='false')
