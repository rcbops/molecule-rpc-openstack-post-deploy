import pytest


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
