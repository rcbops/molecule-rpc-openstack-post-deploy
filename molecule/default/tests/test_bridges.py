# -*- coding: utf-8 -*-
"""ASC-157: Perform Post Deploy System validations"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import testinfra.utils.ansible_runner

# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('network_hosts')[:1]


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc211c-432a-11e8-a091-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1176')
def test_bridges_have_open_ports(host):
    """Ensure OpenVSwitch bridges have at least 2 open ports.

    Args:
        host(testinfra.host.Host): Testinfra host fixture.
    """

    cmd = 'ovs-vsctl list-br'
    bridge_res = host.run(cmd)
    bridges = filter(None, bridge_res.stdout.split('\n'))
    for bridge in bridges:
        cmd = "ovs-vsctl list-ports {} | wc -l".format(bridge)
        res = host.run(cmd)
        assert res.rc == 0
        assert int(res.stdout.strip()) >= 2
