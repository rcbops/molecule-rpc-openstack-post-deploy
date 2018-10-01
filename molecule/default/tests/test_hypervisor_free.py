import os
import testinfra.utils.ansible_runner
import pytest
import json

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('infra1')
cpu_ratio = 1
ram_ratio = 1
disk_ratio = 1


@pytest.mark.test_id('d7fc4ff0-432a-11e8-aca5-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_get_nova_allocation_ratios(host):
    """Retrieve resource allocation ratios from nova_conductor host.

    Resource allocation ratio values are obtained from the nova_conductor host
    and stored as global variables for use by other tests.
    """
    global cpu_ratio
    global ram_ratio
    global disk_ratio

    os_pre = ("lxc-attach -n $(lxc-ls -1 | grep nova_conductor | head -n 1) "
              "-- bash -c \" ")
    cmd = ' '.join(["awk -F= '/^cpu_allocation_ratio/ {print $2}'",
                    "/etc/nova/nova.conf"])
    cpu_res = host.run("{} {}\"".format(os_pre, cmd))
    cmd = ' '.join(["awk -F= '/^ram_allocation_ratio/ {print $2}'",
                    "/etc/nova/nova.conf"])
    ram_res = host.run("{} {}\"".format(os_pre, cmd))
    cmd = ' '.join(["awk -F= '/^disk_allocation_ratio/ {print $2}'",
                    "/etc/nova/nova.conf"])
    disk_res = host.run("{} {}\"".format(os_pre, cmd))
    cpu_ratio = (1 if not cpu_res.stdout.strip().replace(".", "", 1).isdigit()
                 else (float)(cpu_res.stdout)
                 )
    ram_ratio = (1 if not ram_res.stdout.strip().replace(".", "", 1).isdigit()
                 else (float)(ram_res.stdout)
                 )
    disk_ratio = (1 if not disk_res.stdout.strip().replace(".", "", 1).isdigit()
                  else (float)(disk_res.stdout)
                  )
    assert cpu_res.rc == 0
    assert ram_res.rc == 0
    assert disk_res.rc == 0


@pytest.mark.test_id('d7fc518c-432a-11e8-9015-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_hypervisor_free(host):
    """Validate the resource levels for hypervisor"""

    global cpu_ratio
    global ram_ratio
    global disk_ratio

    os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
              "-- bash -c '. /root/openrc ; openstack ")
    cmd = "{} hypervisor stats show -f json'".format(os_pre)
    res = host.run(cmd)
    stats = json.loads(res.stdout)
    assert res.rc == 0
    assert "memory_mb" in stats
    assert "memory_mb_used" in stats
    assert "vcpus" in stats
    assert "vcpus_used" in stats
    assert "free_disk_gb" in stats
    assert ((stats['memory_mb']) * ram_ratio -
            (stats['memory_mb_used'])) / 1024 > 0
    assert (stats['vcpus'] * cpu_ratio - stats['vcpus_used']) > 0
    assert (stats['free_disk_gb'] * disk_ratio) > 0
