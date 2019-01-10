import pytest_rpc_helpers as helpers
import os
import testinfra.utils.ansible_runner
import pytest
import json

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(helpers.cli_host)


@pytest.fixture
def get_nova_allocation_ratios(host):
    """Retrieve resource allocation ratios from nova_conductor host.

    Args:
        host (testinfra.Host): Testinfra host object to execute the action on.

    Returns:
        dict: Ratios
    """

    # NOTE: As of pike, the values in the nova.conf file are ignored and
    # hardcoded as noted in the following document:
    # https://docs.openstack.org/ocata/config-reference/compute/config-options.html
    cpu_default = 1.0
    ram_default = 1.0
    disk_default = 1.0

    # For RPC the config is given the 'nova_conductor' role.  For OSP this
    # config is defined on the director which is the same as the defined
    # cli_host.

    cmd = ' '.join(["awk -F= '/^cpu_allocation_ratio/ {print $2}'",
                    "/etc/nova/nova.conf"])
    cpu_res = host.run(cmd)
    cmd = ' '.join(["awk -F= '/^ram_allocation_ratio/ {print $2}'",
                    "/etc/nova/nova.conf"])
    ram_res = host.run(cmd)
    cmd = ' '.join(["awk -F= '/^disk_allocation_ratio/ {print $2}'",
                    "/etc/nova/nova.conf"])
    disk_res = host.run(cmd)
    cpu_ratio = (cpu_default if not cpu_res.stdout.strip().replace(".", "", 1).isdigit()
                 else (float)(cpu_res.stdout)
                 )
    ram_ratio = (ram_default if not ram_res.stdout.strip().replace(".", "", 1).isdigit()
                 else (float)(ram_res.stdout)
                 )
    disk_ratio = (disk_default if not disk_res.stdout.strip().replace(".", "", 1).isdigit()
                  else (float)(disk_res.stdout)
                  )

    ratios = {
        'cpu_ratio': cpu_ratio,
        'ram_ratio': ram_ratio,
        'disk_ratio': disk_ratio
    }

    return ratios


@pytest.mark.test_id('d7fc518c-432a-11e8-9015-6a00035510c0')
@pytest.mark.jira('asc-157', 'ASC-1257')
def test_hypervisor_free(get_nova_allocation_ratios, host):
    """Validate the resource levels for hypervisor"""

    cmd = "{} hypervisor stats show -f json".format(helpers.os_pre)
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
