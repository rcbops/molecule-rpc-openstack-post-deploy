import os
import pytest
import re
import testinfra.utils.ansible_runner
import pdb


"""ASC-238: Verify the quotas have been configured properly

RPC 10+ manual test 8
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nova_compute')[:1]

pre_cmd = "bash -c \"source /root/openrc; "


@pytest.mark.jira('asc-238')
def test_to_update_tenant_quotas_1st_time(host):
    """Configurate service tenant quotas and verify it works properly at the first time"""

    update_quotas(host, name='tenant', instances=9, cores=8, ram=32)

    verify_updated_quotas(host, name='tenant', instances=9, cores=8, ram=32)


@pytest.mark.jira('asc-238')
def test_to_update_tenant_quotas_2nd_time(host):
    """Configurate service tenant quotas and verify it works properly the second time"""

    update_quotas(host, name='tenant', instances=18, cores=16, ram=64)

    verify_updated_quotas(host, name='tenant', instances=18, cores=16, ram=64)


@pytest.mark.jira('asc-238')
def test_to_update_user_quotas_1st_time(host):
    """Configurate user 'nova' quotas and verify it works properly at the first time"""

    update_quotas(host, name='user', instances=5, cores=10, ram=128)

    verify_updated_quotas(host, name='user', instances=5, cores=10, ram=128)


@pytest.mark.jira('asc-238')
def test_to_update_user_quotas_2nd_time(host):
    """Configurate user 'nova' quotas and verify it works properly at the second time"""

    update_quotas(host, name='user', instances=7, cores=12, ram=256)

    verify_updated_quotas(host, name='user', instances=7, cores=12, ram=256)


def update_quotas(run_on_host, name, instances, cores, ram):
    id = get_id(run_on_host, name)

    cmd = pre_cmd + "nova quota-update --instances " + str(instances) + \
          " --cores " + str(cores) + " --ram " + str(ram) + " " + str(id) + "\""
    run_on_host.run_expect([0], cmd)


def verify_updated_quotas(run_on_host, name, instances, cores, ram):
    id = get_id(run_on_host, name)
    cmd = pre_cmd + "nova quota-show --" + name + " " + id + "\""
    output = run_on_host.run(cmd)
    assert get_quota('instances', output.stdout) == instances
    assert get_quota('cores', output.stdout) == cores
    assert get_quota('ram', output.stdout) == ram


def get_id(run_on_host, name):
    if name == 'tenant':
        # test with tenant 'service'
        cmd = pre_cmd + "openstack project list | grep service\""
    elif name == 'user':
        # test with user 'nova':
        cmd = pre_cmd + "openstack user list | grep nova\""

    output = run_on_host.run(cmd)
    result = re.search(r'(?<=\s)[a-zA-Z0-9]+(?=\s)', output.stdout)
    return result.group(0)


def get_quota(quota_name, quota_show_output):
    quota_name_regex = re.escape(quota_name) + r'(\s+\|\s+[0-9]+\s)'
    if quota_name in quota_show_output:
        # Getting the line of quota, such as 'instances                   | 9'
        line = re.search(quota_name_regex, quota_show_output)
        quota_line = line.group(0)

        # Getting the quota number
        result = re.search(r'(?<=\s)[0-9]+(?=\s)', quota_line)
        return int(result.group(0))
