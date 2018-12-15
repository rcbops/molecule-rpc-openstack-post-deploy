# -*- coding: utf-8 -*-
"""ASC-240: Verify the requested glance images were uploaded

RPC 10+ manual test 10
"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc612b-432a-11e8-9a7a-6a00035510c0')
@pytest.mark.jira('asc-240')
def test_verify_glance_image(os_api_conn):
    """Verify the glance images created by the "os_service_setup.yml" playbook.

    Args:
        os_api_conn (openstack.connection.Connection): Authorized API connection
            to the 'default' cloud on the OpenStack infrastructure.
    """

    images = ['Ubuntu 14.04 LTS',
              'Ubuntu 16.04',
              'Fedora 27',
              'CentOS 7',
              'OpenSuse Leap 42.3',
              'Debian 9 Latest',
              'Debian TESTING',
              'Cirros-0.3.5']

    for image in images:
        assert os_api_conn.get_image_name(image) == image


@pytest.mark.test_id('d7fc62c7-432a-11e8-8102-6a00035510c0')
@pytest.mark.jira('asc-240')
def test_verify_vm_flavors(os_api_conn):
    """Verify the VM flavor created by the "os_service_setup.yml" playbook.

    Args:
        os_api_conn (openstack.connection.Connection): Authorized API connection
            to the 'default' cloud on the OpenStack infrastructure.
    """

    flavors = ['m1.micro',
               'm1.tiny',
               'm1.mini',
               'm1.small',
               'm1.medium',
               'm1.large',
               'm1.xlarge',
               'm1.heavy']

    for flavor in flavors:
        assert os_api_conn.get_flavor_name(flavor) == flavor
