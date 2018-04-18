import os
import testinfra.utils.ansible_runner
import pytest

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('network_hosts')[:1]


@pytest.mark.test_id('d7fc23f5-432a-11e8-9b6d-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_for_dead_taps(host):
    """Ensure there are no dead tap interfaces in OpenVSwitch"""

    cmd = 'ovs-vsctl show'
    res = host.run(cmd)
    assert res.rc == 0
    assert "tag: 4095" not in res.stdout
