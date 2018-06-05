import os
import pytest
import testinfra.utils.ansible_runner
import json

"""ASC-256: Verify Cinder volume creation.

RPC 10+ manual test 14.
"""


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


@pytest.mark.test_id('02a17d7d-4a42-11e8-bdcf-6a00035510c0')
@pytest.mark.jira('asc-256')
def test_cinder_volume_created(host):
    """Verify cinder volume can be created"""

    # Create a test volume
    test_volume_name = "test_volume_compute1"
    cmd1 = "{} openstack volume create --size 1 {}'".format(utility_container, test_volume_name)
    host.run_expect([0], cmd1)

    # Verify the volume is created
    cmd2 = "{} openstack volume list -f json'".format(utility_container)
    res = host.run(cmd2)
    volumes = json.loads(res.stdout)
    volume_names = [d['Name'] for d in volumes]
    assert test_volume_name in volume_names
