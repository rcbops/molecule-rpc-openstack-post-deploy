# -*- coding: utf-8 -*-
"""ASC-157: Perform Post Deploy System validations"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import testinfra.utils.ansible_runner
from configparser import ConfigParser, NoOptionError

# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nova_compute')[:1]


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture
def nova_alloc_ratios(host):
    """Retrieve resource allocation ratios from 'nova_compute' host.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.

    Returns:
        dict: Ratios
    """

    # Setup
    nova_conf_raw_file = host.file('/etc/nova/nova.conf').content_string
    conf = ConfigParser()
    conf.read_string(nova_conf_raw_file)
    ratios = {}

    try:
        ratios['cpu_ratio'] = conf.getfloat('DEFAULT', 'cpu_allocation_ratio')
    except NoOptionError:
        ratios['cpu_ratio'] = 1.0

    try:
        ratios['ram_ratio'] = conf.getfloat('DEFAULT', 'ram_allocation_ratio')
    except NoOptionError:
        ratios['ram_ratio'] = 1.0

    try:
        ratios['disk_ratio'] = conf.getfloat('DEFAULT', 'disk_allocation_ratio')
    except NoOptionError:
        ratios['disk_ratio'] = 1.0

    return ratios


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc518c-432a-11e8-9015-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1318')
def test_hypervisor_free(os_api_conn, nova_alloc_ratios):
    """Validate the resource levels for hypervisor

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        nova_alloc_ratios (dict): Resource allocation ratios from 'nova_compute'
            host.
    """

    # Setup
    # noinspection PyUnresolvedReferences
    hypervisors = [hv.to_dict()
                   for hv in os_api_conn.compute.hypervisors(details=True)]

    # Expect
    expected_stats = ['memory_size',
                      'memory_used',
                      'vcpus',
                      'vcpus_used',
                      'disk_available']

    # Test
    for hypervisor in hypervisors:
        for expected_stat in expected_stats:
            assert expected_stat in hypervisor

        assert ((hypervisor['memory_size']) * nova_alloc_ratios['ram_ratio']
                - (hypervisor['memory_used'])) / 1024 > 0
        assert (hypervisor['vcpus'] * nova_alloc_ratios['cpu_ratio']
                - hypervisor['vcpus_used']) > 0
        assert (hypervisor['disk_available']
                * nova_alloc_ratios['disk_ratio']) > 0
