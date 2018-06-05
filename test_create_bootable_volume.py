import utils
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


@pytest.mark.test_id('3c469966-4fcb-11e8-a604-6a0003552100')
@pytest.mark.jira('asc-258')
def test_create_bootable_volume(host):
    """Test to verify that a bootable volume can be created based on a Glance image

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    null = None
    false = False
    volume_name = 'test_volume'
    image_name = 'Cirros-0.3.5'

    image_id = utils.get_image_id(image_name, host)

    data = {
        "volume": {
            "size": 3,
            "availability_zone": null,
            "source_volid": null,
            "description": null,
            "multiattach": false,
            "snapshot_id": null,
            "backup_id": null,
            "name": volume_name,
            "imageRef": image_id,
            "volume_type": null,
            "metadata": {},
            "consistencygroup_id": null
        }
    }

    utils.create_bootable_volume(data, host)

    utils.verify_volume(volume_name, host)

    # Tear down
    utils.delete_volume(volume_name, host)
