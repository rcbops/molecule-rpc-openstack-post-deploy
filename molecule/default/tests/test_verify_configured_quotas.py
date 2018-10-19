import os
import pytest
import re
import testinfra.utils.ansible_runner


"""ASC-238: Verify the quotas have been configured properly

RPC 10+ manual test 8
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")
tenant = 'service'


@pytest.mark.test_id('d7fc6780-432a-11e8-9c23-6a00035510c0')
@pytest.mark.jira('asc-238')
def test_update_quotas_1st_time_using_id(host):
    """Configurate tenant quotas and verify it works properly at the first time"""

    id = get_tenant_id(tenant, host)
    update_quotas(host, name=id, instances=9, cores=8, ram=32)
    verify_updated_quotas(host, name=id, instances=9, cores=8, ram=32)


@pytest.mark.test_id('43e5e78c-4335-11e8-9508-6a00035510c0')
@pytest.mark.jira('asc-238')
def test_update_quotas_2nd_time_using_id(host):
    """Configurate tenant quotas and verify it works properly the second time"""

    id = get_tenant_id(tenant, host)
    update_quotas(host, name=id, instances=18, cores=16, ram=64)

    verify_updated_quotas(host, name=id, instances=18, cores=16, ram=64)


@pytest.mark.test_id('43e5eade-4335-11e8-942b-6a00035510c0')
@pytest.mark.jira('asc-238')
def test_update_quotas_1st_time_using_name(host):
    """Configurate tenant quotas and verify it works properly at the first time"""

    update_quotas(host, name=tenant, instances=12, cores=10, ram=128)

    verify_updated_quotas(host, name=tenant, instances=12, cores=10, ram=128)


@pytest.mark.test_id('43e5ec59-4335-11e8-af11-6a00035510c0')
@pytest.mark.jira('asc-238')
def test_update_quotas_2nd_time_using_name(host):
    """Configurate service tenant quotas and verify it works properly the second time"""

    update_quotas(host, name=tenant, instances=30, cores=20, ram=256)

    verify_updated_quotas(host, name=tenant, instances=30, cores=20, ram=256)


def update_quotas(run_on_host, name, instances, cores, ram):
    """Update quote using openstack cli 'openstack quota set'"""
    cmd = "{} openstack quota set --instances {} --cores {} --ram {} {}'".format(utility_container, instances, cores, ram, name)
    run_on_host.run_expect([0], cmd)


def verify_updated_quotas(run_on_host, name, instances, cores, ram):
    """Verify updated quotas using openstack cli 'openstack quota show <PROJECT_NAME|PROJECT_ID>'"""
    cmd = "{} openstack quota show {}'".format(utility_container, name)
    output = run_on_host.run(cmd)
    assert get_quota('instances', output.stdout) == instances
    assert get_quota('cores', output.stdout) == cores
    assert get_quota('ram', output.stdout) == ram


def get_tenant_id(tenant_name, run_on_host):
    """Get tenant id associated with tenant name"""
    cmd = "{} openstack project list | grep {}'".format(utility_container, tenant_name)
    output = run_on_host.run(cmd)
    result = re.search(r'(?<=\s)[a-zA-Z0-9]+(?=\s)', output.stdout)
    return result.group(0)


def get_quota(quota_name, quota_show_output):
    """get quota for each quota name"""
    quota_name_regex = re.escape(quota_name) + r'(\s+\|\s+[0-9]+\s)'
    if quota_name in quota_show_output:
        # Getting the line of quota, such as 'instances                   | 9'
        line = re.search(quota_name_regex, quota_show_output)
        quota_line = line.group(0)
        # Getting the quota number
        result = re.search(r'(?<=\s)[0-9]+(?=\s)', quota_line)
        return int(result.group(0))
