import os
import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cinder_volume')


def test_cinder_service(skiptesthost):
    cmd = "sudo bash -c \"source /root/openrc; cinder service-list\""
    output = skiptesthost.run(cmd)
    assert ("cinder-volume" in output.stdout)


def test_cinder_lvm_volume(host):
    output = host.run('vgs cinder-volumes')
    assert re.search("cinder-volumes\s+[0-9]*\s+[0-9]*\s+", output.stdout)


def test_cinder_volume_group(host):
    output = host.run('grep volume_group /etc/cinder/cinder.conf')
    assert ("SUCCESS" in output.stdout)
    assert ("volume_group=cinder-volumes" in output.stdout)
