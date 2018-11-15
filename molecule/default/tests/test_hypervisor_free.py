import os
import testinfra.utils.ansible_runner
import pytest
import json

"""ASC-157: Perform Post Deploy System validations"""

# TODO: Put these values into ansible facts
cli_host = 'director'
cli_openrc_path = '/home/stack/overcloudrc'

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(cli_host)

os_pre = ". {} ; openstack ".format(cli_openrc_path)


@pytest.fixture
def get_nova_allocation_ratios(host):
    """Retrieve resource allocation ratios from nova_conductor host.

    Args:
        host (testinfra.Host): Testinfra host object to execute the action on.

    Returns:
        dict: Ratios
    """

    # There is no 'nova_conductor' role in the OSP inventory.
    # Hard code the ratios to 2

    ratios = {
        'cpu_ratio': 2,
        'ram_ratio': 2,
        'disk_ratio': 2
    }

    return ratios


@pytest.mark.test_id('d7fc518c-432a-11e8-9015-6a00035510c0')
@pytest.mark.jira('asc-157', 'ASC-1257')
def test_hypervisor_free(get_nova_allocation_ratios, host):
    """Validate the resource levels for hypervisor"""

    cmd = "{} hypervisor stats show -f json".format(os_pre)
    res = host.run(cmd)
    stats = json.loads(res.stdout)
    assert res.rc == 0
    assert "memory_mb" in stats
    assert "memory_mb_used" in stats
    assert "vcpus" in stats
    assert "vcpus_used" in stats
    assert "free_disk_gb" in stats
    assert ((stats['memory_mb']) * get_nova_allocation_ratios['ram_ratio']
            - (stats['memory_mb_used'])) / 1024 > 0
    assert (stats['vcpus'] * get_nova_allocation_ratios['cpu_ratio']
            - stats['vcpus_used']) > 0
    assert (stats['free_disk_gb']
            * get_nova_allocation_ratios['disk_ratio']) > 0
