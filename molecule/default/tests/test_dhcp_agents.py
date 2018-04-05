import os
import testinfra.utils.ansible_runner
import pytest

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('dashboard_hosts')


@pytest.mark.jira('asc-157')
def test_openvswitch(host):
    """
    Ensure DHCP agents for all networks are up

    Assumes that results are returned in the following format:
    +--------------+------------+------------+-------------------+-------+-------+--------------------+
    | ID           | Agent Type | Host       | Availability Zone | Alive | State | Binary             |
    +--------------+------------+------------+-------------------+-------+-------+--------------------+
    | <network-id> | DHCP agent | <hostname> | nova              | :-)   | UP    | neutron-dhcp-agent |
    +--------------+------------+------------+-------------------+-------+-------+--------------------+
    """

    os_pre = '. /root/openrc ; '
    net = os_pre + "openstack network list | awk '/[0-9]/ {print $2}'"
    netres = host.run(net)
    networks = netres.stdout.split('\n')
    for network in networks:
        cmd = os_pre + 'openstack network agent list --network "' + network + '"'
        res = host.run(cmd)
        assert "UP" in res.stdout
