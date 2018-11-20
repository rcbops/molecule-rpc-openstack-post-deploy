import os
import testinfra.utils.ansible_runner
import pytest

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('network_hosts')[:1]


@pytest.mark.test_id('a095144a-e767-11e8-aecd-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_ovs_bridges(host):
    """Ensure OpenVSwitch bridges have at least 2 open ports"""

    cmd = 'ovs-vsctl list-br'
    bridge_res = host.run(cmd)
    bridges = filter(None, bridge_res.stdout.split('\n'))
    for bridge in bridges:
        cmd = 'ovs-vsctl list-ports ' + bridge + ' | wc -l'
        res = host.run(cmd)
        assert res.rc == 0
        assert (int)(res.stdout.strip()) >= 2
