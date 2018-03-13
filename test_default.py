import os
import re
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cinder_volume')


@pytest.mark.jira('asc-222')
@pytest.mark.skip(reason='this test can not run on storage host')
# TODO: will update the test to run cinder command on controller node
# TODO: since the test cannot run on storage hosts.
def test_cinder_service(host):
    """Test to verify that cinder service is running on the cinder nodes

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    cmd = "sudo bash -c \"source /root/openrc; cinder service-list\""
    output = host.run(cmd)
    assert ("cinder-volume" in output.stdout)


@pytest.mark.jira('asc-222')
def test_cinder_lvm_volume(host):
    """Test 2a: Check the Cinder Nodes: volume group

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    output = host.run('vgs cinder-volumes')
    assert re.search("cinder-volumes\s+[0-9]*\s+[0-9]*\s+", output.stdout)


@pytest.mark.jira('asc-222')
def test_cinder_volume_group(host):
    """Test 2a: Check the Cinder config file

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    assert host.file('/etc/cinder/cinder.conf').contains("volume_group")


@pytest.mark.jira('asc-222')
@pytest.mark.skip(reason='This test is only for bare metal')
# TODO: 1. This test is only for bare metal
# TODO: 2. This test must be executed on compute_hosts (not storage_hosts)
def test_list_lxc_volume_group(host):
    """Test 2b:
    Check Compute hosts LVM setup and verify we're not leaving an excess of free extents.
    Notes: makes sure if you are using LVM for your partitioning, that all
    available disk space, past the amount needed for the OS, has been allocated
    to /var/lib/nova

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    assert host.run_expect([0], 'vgs lxc')
    # More assertions need to be implemented here


@pytest.mark.jira('asc-222')
@pytest.mark.skip(reason='This test is only for bare metal')
def test_list_lxc_logical_volume(host):
    """Test 2b:
    Check Compute hosts LVM setup and verify we're not leaving an excess of free extents.
    Notes: makes sure if you are using LVM for your partitioning, that all
    available disk space, past the amount needed for the OS, has been allocated
    to /var/lib/nova

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    assert host.run_expect([0], 'lvs lxc')
    # More assertions need to be implemented here


@pytest.mark.jira('asc-222')
@pytest.mark.skip(reason='This test is only for bare metal')
def test_list_free_extents(host):
    """Test 2b:
    Check Compute hosts LVM setup and verify we're not leaving an excess of free extents.
    Notes: makes sure if you are using LVM for your partitioning, that all
    available disk space, past the amount needed for the OS, has been allocated
    to /var/lib/nova

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """
    cmd = "vgs -o -pv_count,lv_count,snap_count,vg_attr,vg_size,vg_free " \
          "-o +vg_free_count"
    output = host.run(cmd)
    # The output will show number of free extents in the second column
    # By default, an physical extent has 4MB, but it can be configurable
    assert ("not many extented found" in output)


@pytest.mark.jira('asc-222')
@pytest.mark.skip(reason='This test is only for bare metal')
# TODO: 1. This test is only for bare metal
# TODO: 2. This test must be executed on compute_hosts (not storage_hosts)
def test_check_cinder_volumes_in_user_config_file(host):
    """Test 2c:
    Check /etc/openstack_deploy/openstack_user_config.yml to make sure
    Cinder is using proper 'cinder-volumes' group, and not 'lxc'
    In other word: just makes sure that if a host has two scsi devices,
    a small one for lxc (lxc group usually) and a larger one for
    cinder-volumes group On actual hardware the 1st scsi device is for
    the OS and configured as RAID 1 where the rest is RAID 10 for compute
    nodes and cinder nodes in order to maximize disk space and IO

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    assert host.file('/etc/openstack_deploy/openstack_user_config.yml')\
        .contains('something')
