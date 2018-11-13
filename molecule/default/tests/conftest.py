# -*- coding: utf-8 -*-
# =============================================================================
# Imports
# =============================================================================
import pytest
import openstack


# =============================================================================
# Fixtures
# =============================================================================
@pytest.fixture
def os_api_connection():
    """Provide an authorized API connection to the 'default' cloud on the OpenStack infrastructure.
    Returns:
        openstack.connection.Connection
    """
    return openstack.connect(cloud='default')


@pytest.fixture
def openstack_properties(host):
    """ this fixture returns a static dictionary of data used for creating
    openstack server (instance)"""
    vars = host.ansible('include_vars', 'file=./vars/main.yml')['ansible_facts']

    os_properties = {
        'image_name': 'Cirros-0.3.5',
        'network_name': vars['gateway_network'],
        'private_net': vars['private_network'],
        'flavor': 'm1.tiny',
        'zone': 'nova'
    }
    return os_properties
