# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import pytest
import openstack


# ==============================================================================
# Fixtures
# ==============================================================================
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

    os_props = host.ansible('include_vars',
                            'file=./vars/main.yml')['ansible_facts']

    return os_props


@pytest.fixture(scope='session')
def os_api_conn():
    """Provide an authorized API connection to the 'default' cloud on the
    OpenStack infrastructure.

    Returns:
        openstack.connection.Connection
    """

    return openstack.connect(cloud='default')
