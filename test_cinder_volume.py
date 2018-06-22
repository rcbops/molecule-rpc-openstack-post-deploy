import os
import pytest
import testinfra.utils.ansible_runner
import utils

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
    random_str = utils.generate_random_string(4)
    volume_name = "test_volume_{}".format(random_str)
    cmd = "{} openstack volume create --size 1 --availability-zone nova {}'".format(utility_container, volume_name)
    host.run_expect([0], cmd)

    # Verify the volume is created
    assert volume_name in utils.openstack_name_list('volume', host)

    # Tear down
    utils.delete_volume(volume_name, host)
