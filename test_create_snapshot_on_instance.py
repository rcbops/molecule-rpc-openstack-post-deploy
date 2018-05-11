import utils
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nova_compute')[:1]


@pytest.mark.test_id('26aa7902-53da-11e8-96e0-6a0003552100')
@pytest.mark.jira('asc-259')
def test_create_instance_from_image(host):

    # Create instance
    image_name = 'CentOS 7'
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
        "from_source": 'snapshot',
        "source_name": snapshot_name,
        "flavor": flavor,
        "network_name": network,
    }

    utils.create_instance(data_image, host)
    utils.verify_if_exist('server', instance_name, host)

    # Shutdown the newly created instance
    utils.shut_it_off('server', instance_name, host)

    # Verify that the instance is shutdown
    assert ("SHUTOFF" == utils.get_status_by_name('server', instance_name, host))

    # Create snapshot from newly created/shutdown instance
    utils.create_snapshot_from_instance(snapshot_name, instance_name, host)

    # Verify the snapshot is successfully created:
    assert ("available" == utils.get_status_by_name('volume', snapshot_name, host))

    # Boot new instance using the newly created snapshot:
    utils.create_instance(data_snapshot, host)

    # Tear down:
    utils.delete_instance(instance_name, host)
    utils.shut_it_off('server', new_instance_name, host)
    utils.delete_instance(new_instance_name, host)
