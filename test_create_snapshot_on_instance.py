import utils
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


@pytest.mark.test_id('26aa7902-53da-11e8-96e0-6a0003552100')
@pytest.mark.jira('asc-259')
def test_create_instance_from_image(host):

    # Create instance
    image_name = 'Cirros-0.3.5'
    flavor = 'm1.tiny'
    network = 'PRIVATE_NET'
    instance_name = 'test_instance_01'
    new_instance_name = 'test_instance_02'
    snapshot_name = 'test_snapshot_02'

    data_image = {
        "instance_name": instance_name,
        "from_source": 'image',
        "source_name": image_name,
        "flavor": flavor,
        "network_name": network,
    }

    data_snapshot = {
        "instance_name": new_instance_name,
        "from_source": 'image',
        "source_name": snapshot_name,
        "flavor": flavor,
        "network_name": network,
    }

    utils.create_instance(data_image, host)
    utils.verify_asset_in_list('server', instance_name, host)

    # Verify the new instance is ACTIVE.
    utils.get_expected_status('server', instance_name, "ACTIVE", host)

    # Shutdown the newly created instance
    utils.stop_server_instance(instance_name, host)

    # Verify that the instance is shutdown
    utils.get_expected_status('server', instance_name, "SHUTOFF", host)

    # Create snapshot from newly created/shutdown instance
    utils.create_snapshot_from_instance(snapshot_name, instance_name, host)

    # Verify the snapshot is successfully created:
    utils.get_expected_status('image', snapshot_name, 'active', host)

    # Boot new instance using the newly created snapshot:
    utils.create_instance(data_snapshot, host)

    # Verify the new instance is successfully booted using the snapshot
    utils.get_expected_status('server', new_instance_name, "ACTIVE", host)

    # Tear down:
    utils.delete_it('server', instance_name, host)
    utils.stop_server_instance(new_instance_name, host)
    utils.delete_it('server', new_instance_name, host)
    utils.delete_it('image', snapshot_name, host)
