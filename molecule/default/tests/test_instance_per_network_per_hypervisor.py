import os
import testinfra.utils.ansible_runner
import pytest
import random
import json
import time

"""ASC-241: Per network, spin up an instance on each hypervisor, perform
external ping, and tear-down """

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
          "-- bash -c '. /root/openrc ; openstack ")
os_post = "'"


@pytest.fixture
def create_server_on(target_host, image_id, flavor, network_id, compute_zone, server_name):
    cmd = "{} server create \
           -f json \
           --image {} \
           --flavor {} \
           --nic net-id={} \
           --availability-zone {} \
           {} {}".format(os_pre, image_id, flavor,
                         network_id, compute_zone, server_name, os_post)
    res = target_host.run(cmd)
    server = json.loads(res.stdout)
    yield server
    target_host.run("{} server delete {} {}".format(os_pre, server['id'],
                                                    os_post))


@pytest.fixture
def create_flavor_on(target_host, flavor):
    flavor_cmd = "{} flavor create --ram 512 --disk 10 \
                  --vcpus 1 {} {}".format(os_pre, flavor, os_post)
    target_host.run_expect([0], flavor_cmd)
    yield
    target_host.run("{} flavor delete {} {}".format(os_pre, flavor,
                                                    os_post))


@pytest.mark.test_id('c3002bde-59f1-11e8-be3b-6c96cfdb252f')
@pytest.mark.jira('ASC-241')
def test_hypervisor_vms(host):
    """ASC-241: Per network, spin up an instance on each hypervisor, perform
    external ping, and tear-down """

    server_list = []
    # get image id
    cmd = "{} image list -f json {}".format(os_pre, os_post)
    res = host.run(cmd)
    images = json.loads(res.stdout)
    filtered_images = list(filter(lambda d: 'buntu' in d['Name'], images))
    assert len(filtered_images) > 0
    image = filtered_images[-1]

    cmd = "lxc-ls -1 | egrep 'neutron(_|-)agents' | tail -1"
    res = host.run(cmd)
    container = res.stdout.strip()
    lxc_pre = "lxc-attach -n {} ".format(container)

    r = random.randint(1111, 9999)
    flavor = "rpctest-{}-flavor".format(r)
    create_flavor_on(host, flavor)

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
        # spin up instance per hypervisor
        cmd = "{} compute service list -f json {}".format(os_pre, os_post)
        res = host.run(cmd)
        computes = json.loads(res.stdout)
        for compute in computes:
            if compute['Binary'] == 'nova-compute':
                instance_name = "rpctest-{}-{}-{}".format(r, compute['Host'],
                                                          network_detail['name'])
                server = create_server_on(host, image['ID'], flavor,
                                          network['ID'], compute['Zone'],
                                          instance_name)
                server_list.append(server)

    # sleep to allow servers to boot
    time.sleep(60)

    for server in server_list:
        cmd = "{} server show {} -f json {}".format(os_pre, server['id'],
                                                    os_post)
        res = host.run(cmd)
        s = json.loads(res.stdout)
        assert s['status'] == 'ACTIVE'

        # test ssh
        network_name, ip = s['addresses'].split('=')
        # get network detail (again)
        # This will include network id and subnets.
        cmd = "{} network show {} -f json {}".format(os_pre, network_name,
                                                     os_post)
        res = host.run(cmd)
        network = json.loads(res.stdout)

        # confirm SSH port access
        cmd = "{} -- bash \
               -c 'ip netns exec qdhcp-{} nc -w1 {} 22'".format(lxc_pre,
                                                                network['id'],
                                                                ip)
        res = host.run(cmd)
        assert 'SSH' in res.stdout

        # get gateway ip via subnet detail
        cmd = "{} subnet show {} -f json {}".format(os_pre,
                                                    network['subnets'], os_post)
        res = host.run(cmd)
        sub = json.loads(res.stdout)
        if sub['gateway_ip']:
            # ping out
            cmd = "{} -- bash -c 'ip netns exec qdhcp-{} \
                   ssh -o StrictHostKeyChecking=no rpc_support ubuntu@{} \
                   ping -c1 -w2 8.8.8.8'".format(lxc_pre, network['id'], ip)
            host.run_expect([0], cmd)
