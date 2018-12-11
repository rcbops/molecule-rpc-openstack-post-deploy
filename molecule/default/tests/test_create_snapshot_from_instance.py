import pytest_rpc.helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner
import utils as tmp_var

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")

random_str = helpers.generate_random_string(5)
instance_name = "test_instance_01_{}".format(random_str)
new_instance_name = "test_instance_02_{}".format(random_str)
snapshot_name = "test_snapshot_name_{}".format(random_str)


@pytest.mark.test_id('26aa7902-53da-11e8-96e0-6a0003552100')
@pytest.mark.jira('asc-259', 'asc-691')
@pytest.mark.test_case_with_steps()
class TestCreateSnapshotFromInstance(object):
    def test_create_snapshot_of_an_instance(self, openstack_properties, host):
        """Create an instance and then create snapshot on it"""

        data_image = {
            "instance_name": instance_name,
            "from_source": 'image',
            "source_name": openstack_properties['test_image_name'],
            "flavor": openstack_properties['test_flavor'],
            "network_name": openstack_properties['private_network'],
        }

        helpers.create_instance(data_image, host)

        assert tmp_var.get_expected_value('server',
                                          instance_name,
                                          'status',
                                          'ACTIVE',
                                          host,
                                          retries=40)

        assert tmp_var.get_expected_value('server',
                                          instance_name,
                                          'OS-EXT-STS:power_state',
                                          'Running',
                                          host,
                                          retries=20)

        assert tmp_var.get_expected_value('server',
                                          instance_name,
                                          'OS-EXT-STS:vm_state',
                                          'active',
                                          host,
                                          retries=20)

        # Create snapshot from newly created/shutdown instance
        snapshot_id = helpers.create_snapshot_from_instance(snapshot_name,
                                                            instance_name,
                                                            host)

        # Verify the snapshot is successfully created:
        assert tmp_var.get_expected_value('image',
                                          snapshot_id,
                                          'status',
                                          'active',
                                          host,
                                          retries=20)

    def test_create_instance_from_snapshot(self, openstack_properties, host):

        data_snapshot = {
            "instance_name": new_instance_name,
            "from_source": 'image',
            "source_name": snapshot_name,
            "flavor": openstack_properties['test_flavor'],
            "network_name": openstack_properties['private_network'],
        }

        # Boot new instance using the newly created snapshot:
        instance_id = helpers.create_instance(data_snapshot, host)

        # Verify the new instance is successfully booted using the snapshot
        assert tmp_var.get_expected_value('server',
                                          instance_id,
                                          'status',
                                          'ACTIVE',
                                          host,
                                          retries=20)
