# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import pytest
from pytest_rpc.helpers import expect_os_property


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('3c469966-4fcb-11e8-a604-6a0003552100')
@pytest.mark.jira('ASC-258', 'ASC-1341')
def test_create_bootable_volume(os_api_conn,
                                create_volume,
                                openstack_properties):
    """Test to verify that a bootable volume can be created based on a
    Glance image.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        create_volume (def): A factory function for generating volumes.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    # Create bootable volume.
    test_volume = create_volume(
        size=1,
        image=openstack_properties['cirros_image'],
        bootable=True
    )

    # Validate that image was created successfully.
    assert expect_os_property(retries=3,
                              os_object=test_volume,
                              os_service='volume',
                              os_api_conn=os_api_conn,
                              os_prop_name='is_bootable',
                              expected_value='true')
