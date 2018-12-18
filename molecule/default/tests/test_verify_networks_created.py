import os
import pytest
import testinfra.utils.ansible_runner


"""ASC-239: Verify the correct networks were created

RPC 10+ manual test 9
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


@pytest.mark.test_id('d7fc646b-432a-11e8-b858-6a00035510c0')
@pytest.mark.jira('asc-239')
def test_verify_network_list(host):
    """Verify the neutron network was created"""
    cmd = "{} openstack network list'".format(utility_container)
    output = host.run(cmd)
    networks = ['GATEWAY_NET', 'PRIVATE_NET']

    for network in networks:
        assert network in output.stdout


@pytest.mark.test_id('d7fc65fa-432a-11e8-a2ae-6a00035510c0')
@pytest.mark.jira('asc-239')
def test_verify_subnet_list(host):
    """Verify the neutron subnet was created """
    cmd = "{} openstack subnet list'".format(utility_container)
    output = host.run(cmd)
    subnets = ['GATEWAY_NET_SUBNET', 'RIVATE_NET_SUBNET']

    for subnet in subnets:
        assert subnet in output.stdout
