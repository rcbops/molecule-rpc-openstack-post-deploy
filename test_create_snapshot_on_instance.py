import pytest_rpc.helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner
from time import sleep

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")

random_str = helpers.generate_random_string(5)
instance_name = "test_instance_01_{}".format(random_str)
new_instance_name = "test_instance_02_{}".format(random_str)
image_name = 'Cirros-0.3.5'
snapshot_name = "test_snapshot_name_{}".format(random_str)
private_net = 'PRIVATE_NET'
flavor = 'm1.tiny'


@pytest.mark.test_id('26aa7902-53da-11e8-96e0-6a0003552100')
@pytest.mark.jira('asc-259')
@pytest.mark.skip(reason='WIP')
@pytest.mark.run(order=4)
def test_create_snapshot_of_an_instance(host):
    """Create an instance and then create snapshot on it"""

    data_image = {
        "instance_name": instance_name,
        "from_source": 'image',
        "source_name": image_name,
        "flavor": flavor,
        "network_name": private_net,
    }

    helpers.create_instance(data_image, host)

    # Verify the new instance is ACTIVE.
    assert (helpers.get_expected_value('server', instance_name, 'status', 'ACTIVE', host, 20))

    # TODO: will find out a better way to avoid implicit sleep. 'status' is 'ACTIVE' is not enough to ensure the
    # TODO: instance is ready, there are many instance statuses that might cause the test failed.
    # TODO: run `openstack server show <instance-ID> -f json` to see all the states
    sleep(120)

    # Create snapshot from newly created/shutdown instance
    helpers.create_snapshot_from_instance(snapshot_name, instance_name, host)

    # Verify the snapshot is successfully created:
    assert (helpers.get_expected_value('image', snapshot_name, 'status', 'active', host, 20))


@pytest.mark.test_id('4ca28c34-7e24-11e8-a634-9cdc71d6c128')
@pytest.mark.jira('asc-691')
@pytest.mark.skip(reason='WIP')
@pytest.mark.run(order=5)
def test_create_instance_from_snapshot(host):

    data_snapshot = {
        "instance_name": new_instance_name,
        "from_source": 'image',
        "source_name": snapshot_name,
        "flavor": flavor,
        "network_name": private_net,
    }

    # Boot new instance using the newly created snapshot:
    helpers.create_instance(data_snapshot, host)

    # Verify the new instance is successfully booted using the snapshot
    assert (helpers.get_expected_value('server', new_instance_name, 'status', 'ACTIVE', host, 20))


@pytest.mark.test_id('48fff282-7e25-11e8-a634-9cdc71d6c128')
@pytest.mark.jira('asc-691')
@pytest.mark.skip(reason='WIP')
@pytest.mark.run(order=6)
def test_teardown(host):
    """tear down"""

    helpers.delete_it('server', instance_name, host)
    helpers.delete_it('server', new_instance_name, host)
    helpers.delete_it('image', snapshot_name, host)
