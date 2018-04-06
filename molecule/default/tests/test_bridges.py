import os
import testinfra.utils.ansible_runner
import pytest

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('network_hosts')[:1]


@pytest.mark.jira('asc-157')
def test_for_dead_taps(host):
    """Ensure OpenVSwitch bridges have at least 2 open ports"""

    cmd = 'ovs-vsctl list-br'
    bridge_res = host.run(cmd)
    bridges = filter(None,bridge_res.stdout.split('\n'))
    for bridge in bridges:
        cmd = 'ovs-vsctl list-ports ' + bridge + ' | wc -l'
        res = host.run(cmd)
        assert res.rc == 0
        assert (int)(res.stdout.strip()) >= 2
