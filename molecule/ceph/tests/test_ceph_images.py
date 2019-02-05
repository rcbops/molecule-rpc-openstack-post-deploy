# -*- coding: utf-8 -*-
# =============================================================================
# Imports
# =============================================================================
import os
import pytest
import testinfra.utils.ansible_runner

# =============================================================================
# Globals
# =============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


# =============================================================================
# Test Cases
# =============================================================================
@pytest.mark.test_id('d5d52357-28ae-11e9-95d3-6a00035510c0')
@pytest.mark.jira('ASC-1031')
def test_ceph_images(host):
    """Ensure that ceph images exist on the undercloud controller"""

    vars = host.ansible('include_vars',
                        'file=./vars/main.yml')['ansible_facts']

    undercloudrc = vars['undercloudrc_path']
    undercloud_ssh_key = vars['undercloud_ssh_key']

    ssh_pre = ' '.join(['ssh',
                        '-i ' + undercloud_ssh_key,
                        '-o StrictHostKeyChecking=no',
                        '-o UserKnownHostsFile=/dev/null'])

    rbd_cmd = 'sudo rbd -p images ls'

    os_pre = ". {} ; openstack".format(undercloudrc)
    server = 'overcloud-controller-0'
    cmd = "{} server show -f value -c addresses {}".format(os_pre, server)
    res = host.run(cmd)
    assert res.rc == 0
    controllers = filter(None, res.stdout.split('\n'))
    assert len(controllers) > 0

    controller = next(iter(controllers), None)
    p, controller_ip = controller.split('=')

    cmd = "{} heat-admin@{} '{}'".format(ssh_pre, controller_ip, rbd_cmd)

    res = host.run(cmd)

    assert res.rc == 0
    image_ids = filter(None, res.stdout.split('\n'))
    assert len(image_ids) > 1
