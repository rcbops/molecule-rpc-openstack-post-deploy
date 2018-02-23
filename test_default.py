import os
import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cinder_volume')


def test_cinder_service(host):
    cmd = "sudo bash -c \"source /root/openrc; cinder service-list\""
    output = host.run(cmd)
    assert ("cinder-volume" in output.stdout)


def test_cinder_lvm_volume(host):
    cmd = "sudo bash -c \"source /root/openrc; " \
          "pushd /opt/openstack-ansible; " \
          "ansible storage_hosts -m shell -a 'vgs cinder-volumes'\""
    output = host.run(cmd)
    assert re.search("cinder-volumes\s+[0-9]*\s+[0-9]*\s+", output.stdout)


def test_cinder_volume_group(host):
    cmd = "sudo bash -c \"source /root/openrc; " \
          "pushd /opt/openstack-ansible; " \
          "ansible cinder_volume -m shell -a " \
          "'grep volume_group /etc/cinder/cinder.conf'\""
    output = host.run(cmd)
    assert ("SUCCESS" in output.stdout)
    assert ("volume_group=cinder-volumes" in output.stdout)
