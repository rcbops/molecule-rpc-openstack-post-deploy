import pytest_rpc.helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")

random_str = helpers.generate_random_string(6)
volume_name = "test_volume_{}".format(random_str)
instance_name = "test_instance_{}".format(random_str)
image_name = 'Cirros-0.3.5'
network_name = 'PRIVATE_NET'
flavor = 'm1.tiny'


@pytest.mark.test_id('73c5d0b2-7584-11e8-ba5b-fe14fb7452aa')
@pytest.mark.jira('asc-462')
@pytest.mark.run(order=1)
def test_create_bootable_volume(host):
    """Test to verify that a bootable volume can be created based on a Glance image

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    image_id = helpers.get_id_by_name('image', image_name, host)
    assert image_id is not None

    cmd = "{} openstack volume create --size 1 --image {} --bootable {}'".format(utility_container, image_id, volume_name)
    host.run_expect([0], cmd)

    volumes = helpers.openstack_name_list('volume', host)
    assert volumes
    volume_names = [x['Name'] for x in volumes]
    assert volume_name in volume_names
    assert (helpers.get_expected_value('volume', volume_name, 'status', 'available', host))


@pytest.mark.test_id('8b701dbc-7584-11e8-ba5b-fe14fb7452aa')
@pytest.mark.jira('asc-462')
@pytest.mark.run(order=2)
def test_create_instance_from_bootable_volume(host):
    """Test to verify that a bootable volume can be created based on a Glance image

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """

    volume_id = helpers.get_id_by_name('volume', volume_name, host)
    assert volume_id is not None

    network_id = helpers.get_id_by_name('network', network_name, host)
    assert network_id is not None

    cmd = "{} openstack server create --volume {} --flavor {} --nic net-id={} {}'".format(utility_container, volume_id, flavor, network_id, instance_name)

    host.run_expect([0], cmd)

    instances = helpers.openstack_name_list('server', host)
    assert instances
    instance_names = [x['Name'] for x in instances]
    assert instance_name in instance_names
    assert (helpers.get_expected_value('server', instance_name, 'status', 'ACTIVE', host))
    assert (helpers.get_expected_value('server', instance_name, 'OS-EXT-STS:power_state', 'Running', host))

    # Tear down
    helpers.delete_instance(instance_name, host)
    helpers.delete_volume(volume_name, host)
