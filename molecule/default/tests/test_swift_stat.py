# -*- coding: utf-8 -*-
"""ASC-299: Verify swift endpoint status

See RPC 10+ Post-Deployment QC process document
"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import pytest_rpc.helpers as helpers
import testinfra.utils.ansible_runner


# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc4b42-432a-11e8-9ef9-6a00035510c0')
@pytest.mark.jira('ASC-299', 'RI-519', 'ASC-1327')
def test_verify_swift_stat(host, openstack_properties):
    """Verify the swift endpoint status.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    cmd = 'swift stat -v'

    if openstack_properties['os_version_major'] < 17:
        result = helpers.run_on_swift(cmd, host)
    else:
        # Work around for ASC-1398:
        cmd = ". openrc ; " + cmd

        result = helpers.run_on_container(cmd, 'utility', host)

    assert 'Account: AUTH_' in result.stdout
    assert 'X-Trans-Id: tx' in result.stdout
