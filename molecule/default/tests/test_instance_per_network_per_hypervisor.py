import os
import testinfra.utils.ansible_runner
import pytest
import json
import pytest_rpc.helpers as helpers
from time import sleep

"""ASC-241: Per network, spin up an instance on each hypervisor, perform
external ping, and tear-down """

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]

os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
          "-- bash -c '. /root/openrc ; openstack ")
os_post = "'"


def create_server_on(target_host, image_id, flavor, network_id, compute_zone, server_name):
    cmd = "{} server create \
           -f json \
           --image {} \
           --flavor {} \
           --nic net-id={} \
           --availability-zone {} \
           --key-name 'rpc_support' \
           {} {}".format(os_pre, image_id, flavor,
                         network_id, compute_zone, server_name, os_post)
    res = target_host.run(cmd)
    server = json.loads(res.stdout)
    return server


@pytest.mark.test_id('c3002bde-59f1-11e8-be3b-6c96cfdb252f')
@pytest.mark.jira('ASC-241', 'ASC-883', 'ASC-789', 'RI-417')
def test_hypervisor_vms(host):
    """ASC-241: Per network, spin up an instance on each hypervisor, perform
    external ping, and tear-down """

    ssh = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
           -i ~/.ssh/rpc_support ubuntu@{}"

    vars = host.ansible('include_vars',
                        'file=./vars/main.yml')['ansible_facts']

    flavor_name = vars['flavor']['name']
    image_name = vars['image']['name']

    server_list = []
    testable_networks = []

    # get image id (sounds like a helper, or register it as an ansible value)
    cmd = "{} image list -f json {}".format(os_pre, os_post)
    res = host.run(cmd)
    images = json.loads(res.stdout)
    assert len(images) > 0
    filtered_images = list(filter(lambda d: d['Name'] == image_name, images))
    assert len(filtered_images) > 0
    image = filtered_images[-1]

    # neutron_agent connection lookup
    na_list = testinfra.utils.ansible_runner.AnsibleRunner(
        os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('neutron_agent')
    hostname = host.check_output('hostname')
    na_list = [x for x in na_list if hostname in x]
    neutron_agent = next(iter(na_list), None)
    assert neutron_agent
    if 'container' in neutron_agent:
        # lxc
        na_pre = "lxc-attach -n {} -- bash -c ".format(neutron_agent)
    else:
        # ssh
        na_pre = "ssh -o StrictHostKeyChecking=no \
                   -o UserKnownHostsFile=/dev/null \
                   {} ".format(neutron_agent)

    r = os.urandom(10).encode('hex')

    # get list of internal networks
    net_cmd = "{} network list -f json {}".format(os_pre, os_post)
    net_res = host.run(net_cmd)
    networks = json.loads(net_res.stdout)
    for network in networks:
        cmd = "{} network show {} -f json {}".format(os_pre, network['ID'],
                                                     os_post)
        res = host.run(cmd)
        network_detail = json.loads(res.stdout)
        if network_detail['router:external'] == 'External':
            continue
        testable_networks.append(network_detail)

    if not testable_networks:
        pytest.skip("No testable networks found")

    # iterate over internal networks
    for network in testable_networks:
        # spin up instance per hypervisor
        cmd = "{} compute service list -f json {}".format(os_pre, os_post)
        res = host.run(cmd)
        computes = json.loads(res.stdout)
        for compute in computes:
            if compute['Binary'] == 'nova-compute':
                instance_name = "rpctest-{}-{}-{}".format(r, compute['Host'],
                                                          network['name'])
                server = create_server_on(host, image['ID'], flavor_name,
                                          network['id'], compute['Zone'],
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
        cmd = "{} server show {} -f json {}".format(os_pre, server, os_post)
        res = host.run(cmd)
        server_detail = json.loads(res.stdout)
        network_name, ip = server_detail['addresses'].split('=')
        # get network detail (again)
        # This will include network id and subnets.
        cmd = "{} network show {} -f json {}".format(os_pre, network_name,
                                                     os_post)
        res = host.run(cmd)
        network = json.loads(res.stdout)

        # confirm SSH port access
        cmd = "{} 'ip netns exec \
               qdhcp-{} nc -w1 {} 22'".format(na_pre, network['id'], ip)
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
        cmd = "{} subnet show {} -f json {}".format(os_pre,
                                                    network['subnets'], os_post)
        res = host.run(cmd)
        sub = json.loads(res.stdout)
        if sub['gateway_ip']:
            # ping out
            cmd = "{} 'ip netns exec \
                   qdhcp-{} {} ping -c1 -w2 8.8.8.8'".format(na_pre,
                                                             network['id'],
                                                             ssh.format(ip))
            host.run_expect([0], cmd)
