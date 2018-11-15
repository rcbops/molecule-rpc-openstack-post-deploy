import os
import testinfra.utils.ansible_runner
import pytest
import json

"""ASC-157: Perform Post Deploy System validations"""

# TODO: Put these values into ansible facts
cli_host = 'director'
cli_openrc_path = '/home/stack/overcloudrc'

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(cli_host)

os_pre = ". {} ; openstack ".format(cli_openrc_path)


@pytest.mark.test_id('d7fc25ae-432a-11e8-a20a-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_openvswitch(host):
    """
    Ensure DHCP agents for all networks are up
    """

    net_cmd = "{} network list -f json".format(os_pre)
    net_res = host.run(net_cmd)
    networks = net_res.stdout.split('\n')
    networks = json.loads(net_res.stdout)
    for network in networks:
        net_agent_cmd = "{} network agent list --network {} -f json".format(os_pre, network['ID'])

        print net_agent_cmd
        res = host.run(net_agent_cmd)
        results = json.loads(res.stdout)

        for agent in results:
            assert agent['State'] == 'UP'
