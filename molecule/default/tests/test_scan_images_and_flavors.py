import os
import pytest
import testinfra.utils.ansible_runner


"""ASC-240: Verify the requested glance images were uploaded

RPC 10+ manual test 10
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]

# attach the utility container:
attach_utility_container = ("lxc-attach -n "
                            "`lxc-ls -1 | grep utility | head -n 1` "
                            "-- bash -c ")


@pytest.mark.test_id('d7fc612b-432a-11e8-9a7a-6a00035510c0')
@pytest.mark.jira('asc-240')
def test_verify_glance_image(host):
    """Verify the glance images created by the "os_service_setup.yml" playbook.
    """
    cmd = attach_utility_container + "'. /root/openrc ; openstack image list'"
    output = host.run(cmd)
    images = ['Ubuntu 14.04 LTS',
              'Ubuntu 16.04',
              'Fedora 27',
              'CentOS 7',
              'OpenSuse Leap 42.3',
              'Debian 9 Latest',
              'Debian TESTING',
              'Cirros-0.3.5']

    for image in images:
        assert image in output.stdout


@pytest.mark.test_id('d7fc62c7-432a-11e8-8102-6a00035510c0')
@pytest.mark.jira('asc-240')
def test_verify_vm_flavors(host):
    """Verify the VM flavor created by the "os_service_setup.yml" playbook.
    """
    cmd = attach_utility_container + "'. /root/openrc ; openstack flavor list'"
    output = host.run(cmd)
    flavors = ['m1.micro',
               'm1.tiny',
               'm1.mini',
               'm1.small',
               'm1.medium',
               'm1.large',
               'm1.xlarge',
               'm1.heavy']

    for flavor in flavors:
        assert flavor in output.stdout
