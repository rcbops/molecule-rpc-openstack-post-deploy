# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import pytest
import openstack


# ==============================================================================
# Fixtures
# ==============================================================================
# TODO: these fixtures should be enhanced and moved to 'pytest-rpc'. (ASC-1253)
@pytest.fixture(scope='module')
def openstack_properties(host):
    """This fixture returns a dictionary of OpenStack facts and variables from
    Ansible which can be used to manipulate OpenStack objects. (i.e. create
    server instances)

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json or
            molecule.yml

    Returns:
        dict: a static dictionary of data about OpenStack.
    """

    os_vars = host.ansible('include_vars',
                           'file=./vars/main.yml')['ansible_facts']

    os_properties = {
        'image_name': 'Cirros-0.3.5',
        'network_name': os_vars['gateway_network'],
        'private_net': os_vars['private_network'],
        'glance_nfs_share_path': os_vars['glance_nfs_share_path'],
        'glance_nfs_mount_path': os_vars['glance_nfs_mount_path'],
        'flavor': 'm1.tiny',
        'zone': 'nova'
    }

    return os_properties


@pytest.fixture(scope='session')
def os_api_conn():
    """Provide an authorized API connection to the 'default' cloud on the
    OpenStack infrastructure.

    Returns:
        openstack.connection.Connection
    """

    return openstack.connect(cloud='default')
