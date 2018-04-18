import os
import pytest
import testinfra.utils.ansible_runner


"""ASC-239: Verify the correct networks were created

RPC 10+ manual test 9
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nova_compute')[:1]

pre_cmd = "bash -c \"source /root/openrc; "


@pytest.mark.test_id('d7fc646b-432a-11e8-b858-6a00035510c0')
@pytest.mark.jira('asc-239')
def test_verify_network_list(host):
    """Verify the neutron network was created"""
    cmd = pre_cmd + "openstack network list\""
    output = host.run(cmd)
    assert ("GATEWAY_NET" in output.stdout)
    assert ("PRIVATE_NET" in output.stdout)


@pytest.mark.test_id('d7fc65fa-432a-11e8-a2ae-6a00035510c0')
@pytest.mark.jira('asc-239')
def test_verify_subnet_list(host):
    """Verify the neutron subnet was created """
    cmd = pre_cmd + "openstack subnet list\""
    output = host.run(cmd)
    assert ("GATEWAY_NET_SUBNET" in output.stdout)
    assert ("PRIVATE_NET_SUBNET" in output.stdout)
