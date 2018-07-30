import os
import testinfra.utils.ansible_runner
import pytest
import json
import pytest_rpc.helpers as helpers

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


@pytest.mark.test_id('d7fc25ae-432a-11e8-a20a-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_openvswitch(host):
    """
    Ensure DHCP agents for all networks are up
    """

    osa_name, osa_major = helpers.get_osa_version_tuple()
    try:
        osa_major = int(osa_major)
    except ValueError:
        osa_major = 99

    os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
              "-- bash -c '. /root/openrc ; openstack ")
    net_cmd = "{} network list -f json'".format(os_pre)
    net_res = host.run(net_cmd)
    networks = net_res.stdout.split('\n')
    networks = json.loads(net_res.stdout)
    for network in networks:
        if osa_major > 14:
            net_agent_cmd = "{} network agent list --network {} -f json'".format(os_pre, network['ID'])
        else:
            net_agent_cmd = ("lxc-attach "
                             "-n $(lxc-ls -1 | grep utility | head -n 1) "
                             "-- bash -c '. /root/openrc ; "
                             "neutron dhcp-agent-list-hosting-net {} "
                             "-f json'".format(network['ID']))

        res = host.run(net_agent_cmd)
        results = json.loads(res.stdout)

        for agent in results:
            if osa_major > 14:
                assert agent['State'] is 'UP'
            else:
                assert agent['admin_state_up'] is True
