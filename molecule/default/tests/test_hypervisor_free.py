import os
import testinfra.utils.ansible_runner
import pytest

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('dashboard_hosts')


@pytest.mark.testinfra_hosts(testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nova_conductor'))
def test_get_nova_allocation_ratios(host):
    """Retrieve resource allocation ratios from nova_conductor host.

    Resource allocation ratio values are obtained from the nova_conductor host
    and stored as global variables for use by other tests.
    """
    global cpu_ratio
    global ram_ratio
    global disk_ratio

    cpu_res = host.run(
        "awk -F= '/^cpu_allocation_ratio/ {print $2}' /etc/nova/nova.conf")
    ram_res = host.run(
        "awk -F= '/^ram_allocation_ratio/ {print $2}' /etc/nova/nova.conf")
    disk_res = host.run(
        "awk -F= '/^disk_allocation_ratio/ {print $2}' /etc/nova/nova.conf")
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


@pytest.mark.jira('asc-157')
def test_hypervisor_free(host):
    """Validate the resource levels for hypervisor"""

    openstack_pre = 'bash -c "source /root/openrc; '
    cmd = openstack_pre + ' openstack hypervisor stats show "'
    res = host.run(cmd)
    fields = get_os_output_list(res.stdout)
    fields = filter(lambda x: x[1].isdigit(), fields)
    fields = dict(map(lambda x: (x[0], (int)(x[1])), fields))
    assert res.rc == 0
    assert "memory_mb" in fields
    assert "memory_mb_used" in fields
    assert "vcpus" in fields
    assert "vcpus_used" in fields
    assert "free_disk_gb" in fields
    assert ((fields['memory_mb']) * ram_ratio -
            (fields['memory_mb_used']))/1024 > 0
    assert (fields['vcpus'] * cpu_ratio - fields['vcpus_used']) > 0
    assert (fields['free_disk_gb'] * disk_ratio) > 0


# Helper method
def get_os_output_list(output):
    """Convert Openstack CLI output to a list of key,value tuples.

    Args:
        output(string): The tablular text output from a query to the OpenStack
        CLI interface.

    Returns:
        A list of key, value tuples.
    """

    res = []
    for line in output.split('\n'):
        fields = [x.strip() for x in line.split('|')]
        fields = filter(None, fields)
        if len(fields) == 2:
            res.append((tuple)(fields))
    return res
