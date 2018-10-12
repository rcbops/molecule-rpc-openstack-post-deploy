import os
import pytest
import testinfra.utils.ansible_runner


"""ASC-236: Verify the requested user(s) and tenant(s) were created
and assigned the proper role.

Notes: These tests should be in keystone submodule, however, there
are not many test cases for keystone at this time so we are putting
them here in novo submodule. When the keystone test cases grow in
the future, we should create keystone submodule for them

RPC 10+ manual test 7
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


@pytest.mark.test_id('43e5ef8c-4335-11e8-9995-6a00035510c0')
@pytest.mark.jira('asc-236')
def test_keystone_users(host):
    """Verify the requested users were created"""
    cmd = "{} openstack user list --domain=default'".format(utility_container)
    output = host.run(cmd)
    assert ("cinder" in output.stdout)
    assert ("glance" in output.stdout)
    assert ("heat" in output.stdout)
    assert ("keystone" in output.stdout)
    assert ("neutron" in output.stdout)
    assert ("nova" in output.stdout)


@pytest.mark.test_id('43e5f054-4335-11e8-817d-6a00035510c0')
@pytest.mark.jira('asc-236')
def test_keystone_tenants(host):
    """Verify the service tenant was created """
    cmd = "{} openstack project list'".format(utility_container)
    output = host.run(cmd)
    assert ("service" in output.stdout)
