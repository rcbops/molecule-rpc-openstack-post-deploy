import os
import pytest
import testinfra.utils.ansible_runner
import json

"""ASC-256: Verify Cinder volume creation.

RPC 10+ manual test 14.
"""


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
          "-- bash -c '. /root/openrc ; openstack ")


@pytest.mark.test_id('02a17d7d-4a42-11e8-bdcf-6a00035510c0')
@pytest.mark.jira('asc-256')
def test_cinder_volume_created(host):
    """Verify cinder volume was created"""
    cmd = "{} volume list -f json'".format(os_pre)
    res = host.run(cmd)
    volumes = json.loads(res.stdout)
    volume_names = [d['Name'] for d in volumes]
    assert "test_volume_compute1" in volume_names
