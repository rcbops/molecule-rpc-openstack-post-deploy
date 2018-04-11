import os
import pytest
import testinfra.utils.ansible_runner


"""ASC-240: Verify the requested glance images were uploaded

RPC 10+ manual test 10
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('compute-infra_hosts')[:1]

# attach the utility container:
attach_utility_container = "lxc-attach -n `lxc-ls -1 | grep utility | head -n 1` -- bash -c "


@pytest.mark.jira('asc-240')
def test_verify_glance_image(host):
    """Verify the glance images created by:
    https://github.com/openstack/openstack-ansible-ops/blob/master/multi-node-aio/playbooks/vars/openstack-service-config.yml
    """
    cmd = attach_utility_container + "'. /root/openrc ; openstack image list'"
    output = host.run(cmd)
    assert ("Ubuntu 14.04 LTS" in output.stdout)
    assert ("Ubuntu 16.04" in output.stdout)
    assert ("Fedora 27" in output.stdout)
    assert ("CentOS 7" in output.stdout)
    assert ("OpenSuse Leap 42.3" in output.stdout)
    assert ("Debian 9 Latest" in output.stdout)
    assert ("Debian TESTING" in output.stdout)
    assert ("Cirros-0.3.5" in output.stdout)


@pytest.mark.jira('asc-240')
def test_verify_subnet_list(host):
    """Verify the VM flavor created by:
    https://github.com/openstack/openstack-ansible-ops/blob/master/multi-node-aio/playbooks/vars/openstack-service-config.yml
    """
    cmd = attach_utility_container + "'. /root/openrc ; openstack flavor list'"
    output = host.run(cmd)
    assert ("m1.micro" in output.stdout)
    assert ("m1.tiny" in output.stdout)
    assert ("m1.mini" in output.stdout)
    assert ("m1.small" in output.stdout)
    assert ("m1.medium" in output.stdout)
    assert ("m1.large" in output.stdout)
    assert ("m1.xlarge" in output.stdout)
    assert ("m1.heavy" in output.stdout)
