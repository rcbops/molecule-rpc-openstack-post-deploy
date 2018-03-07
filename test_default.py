import os
import re

import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cinder_volume')


@pytest.mark.skip(reason='TODO: will update the test to run '
                         'cinder command on controller')
def test_cinder_service(host):
    cmd = "sudo bash -c \"source /root/openrc; cinder service-list\""
    output = host.run(cmd)
    assert ("cinder-volume" in output.stdout)


def test_cinder_lvm_volume(host):
    output = host.run('vgs cinder-volumes')
    assert re.search("cinder-volumes\s+[0-9]*\s+[0-9]*\s+", output.stdout)


def test_cinder_volume_group(host):
    assert host.file('/etc/cinder/cinder.conf').contains("volume_group")
