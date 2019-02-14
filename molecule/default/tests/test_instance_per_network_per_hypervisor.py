import os
import testinfra.utils.ansible_runner
import pytest
import random
import json
import pytest_rpc_helpers as helpers
from time import sleep

"""ASC-241: Per network, spin up an instance on each hypervisor, perform
external ping, and tear-down """

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(helpers.cli_host)


def create_server_on(target_host, image_id, flavor, network_id, compute_zone, server_name):
    cmd = ('{0} server create '
           '-f json '
           '--image {1} '
           '--flavor "{2}" '
           '--nic net-id={3} '
           '--availability-zone "{4}" '
           '--key-name rpc_support '
           '--security-group rpc-support '
           '"{5}"').format(helpers.os_pre,
                           image_id,
                           flavor,
                           network_id,
                           compute_zone,
                           server_name)
    res = target_host.run(cmd)
    server = json.loads(res.stdout)
    return server


@pytest.mark.test_id('c3002bde-59f1-11e8-be3b-6c96cfdb252f')
@pytest.mark.jira('ASC-241', 'ASC-883', 'ASC-789', 'RI-417')
def test_hypervisor_vms(host):
    """ASC-241: Per network, spin up an instance on each hypervisor, perform
    external ping, and tear-down """

    ssh = ('ssh -o StrictHostKeyChecking=no '
           '-o UserKnownHostsFile=/dev/null '
           '-i ~/.ssh/rpc_support ubuntu@{}')

    vars = host.ansible('include_vars',
                        'file=./vars/main.yml')['ansible_facts']

    flavor_name = vars['flavor']['name']
    image_name = vars['image']['name']

    server_list = []
    dhcp_networks = []
    testable_networks = []

    # get image id (sounds like a helper, or register it as an ansible value)
    cmd = "{} image list -f json".format(helpers.os_pre)
    res = host.run(cmd)
    images = json.loads(res.stdout)
    assert len(images) > 0
    filtered_images = list(filter(lambda d: d['Name'] == image_name, images))
    assert len(filtered_images) > 0
    image = filtered_images[-1]

    # neutron_agent connection lookup
    # OSP use controller for nova_agent!
    cmd = ('. /home/stack/stackrc && '
           'openstack server show '
           '-f value -c addresses '
           'overcloud-controller-0')
    res = host.run(cmd)
    controller_network_name, controller_ip = res.stdout.split('=')
    assert controller_ip
    na_pre = ('ssh '
              '-i /home/stack/.ssh/id_rsa '
              '-o StrictHostKeyChecking=no '
              '-o UserKnownHostsFile=/dev/null '
              'heat-admin@{0} ').format(controller_ip)

    # Copy rpc_support key to heat-admin account on overcloud-controller-0
    cmd = ('scp '
           '-i /home/stack/.ssh/id_rsa '
           '-o StrictHostKeyChecking=no '
           '-o UserKnownHostsFile=/dev/null '
           '.ssh/rpc_support '
           'heat-admin@{0}:.ssh/').format(controller_ip)
    host.run_expect([0], cmd)

    r = random.randint(1111, 9999)

    # get list of netns dhcp agents
    # search results will be in the following form:
    # 'qdhcp-b51687aa-b4c4-4f20-bab1-cc5d948521ac (id: 2)'
    cmd = ("{0} 'sudo ip netns list'").format(na_pre)
    res = host.run(cmd)
    netns_list = res.stdout.split('\n')
    for netns in netns_list:
        if netns.find('qdhcp') == 0:
            dhcp_networks.append(netns.split(' ')[0][6:])

    # get list of internal networks
    net_cmd = "{} network list -f value -c ID".format(helpers.os_pre)
    net_res = host.run(net_cmd)
    networks = net_res.stdout.split('\n')
    for network in networks:
        cmd = "{} network show {} -f json".format(helpers.os_pre, network)
        res = host.run(cmd)
        network_detail = json.loads(res.stdout)
        if network_detail['router:external'] == 'External':
            continue
        # also have dhcp infrastructure
        if network in dhcp_networks:
            testable_networks.append(network_detail)

    if not testable_networks:
        pytest.skip("No testable networks found")

    # iterate over internal networks
    for network in testable_networks:
        # spin up instance per zone
        zone = 'nova'
        instance_name = "rpctest-{0}-{1}-{2}".format(r, zone,
                                                     network['name'])
        server = create_server_on(host, image['ID'], flavor_name,
                                  network['id'], zone,
                                  instance_name)
        assert helpers.get_expected_value('server', server['id'],
                                          'OS-EXT-STS:power_state', 'Running', host, 15)
        assert helpers.get_expected_value('server', server['id'],
                                          'status', 'ACTIVE', host, 15)
        assert helpers.get_expected_value('server', server['id'],
                                          'OS-EXT-STS:vm_state', 'active', host, 15)
        server_list.append(server['id'])

    for server in server_list:
        # test ssh
        print "DEBUG OUTPUT"
        print server
        cmd = "{} server show {} -f json".format(helpers.os_pre, server)
        res = host.run(cmd)
        server_detail = json.loads(res.stdout)
        network_name, ip = server_detail['addresses'].split('=')
        # get network detail (again)
        # This will include network id and subnets.
        cmd = "{} network show '{}' -f json".format(helpers.os_pre, network_name)
        res = host.run(cmd)
        network = json.loads(res.stdout)

        # confirm SSH port access
        cmd = ("{0} "
               "'echo break | sudo ip netns exec qdhcp-{1} nc -w1 {2} 22'"
               ).format(na_pre, network['id'], ip)
        for attempt in range(30):
            res = host.run(cmd)
            try:
                assert 'SSH' in res.stdout
            except AssertionError:
                sleep(10)
            else:
                break
        else:
            assert 'SSH' in res.stdout

        # get gateway ip via subnet detail
        cmd = "{} subnet show {} -f json".format(helpers.os_pre,
                                                 network['subnets'])
        res = host.run(cmd)
        sub = json.loads(res.stdout)
        if sub['gateway_ip']:
            # ping out
            cmd = ("{0} "
                   "'sudo ip netns exec qdhcp-{1} {2} ping -c1 -w2 8.8.8.8'"
                   ).format(na_pre,
                            network['id'],
                            ssh.format(ip))
            host.run_expect([0], cmd)
