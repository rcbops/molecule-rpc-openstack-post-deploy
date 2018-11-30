import pytest_rpc.helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner
import utils as tmp_var

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


@pytest.fixture
def create_bootable_volume(openstack_properties, host):
    """Test to verify that a bootable volume can be created based on a
    Glance image

    Args:
        openstack_properties (dict): fixture 'openstack_properties' from
        conftest.py
        host(testinfra.host.Host): Testinfra host fixture.
    """

    image_id = helpers.get_id_by_name('image',
                                      openstack_properties['image_name'],
                                      host)
    assert image_id is not None

    random_str = helpers.generate_random_string(6)
    volume_name = "test_volume_{}".format(random_str)

    data = {'volume': {'size': '1',
                       'imageref': image_id,
                       'name': volume_name,
                       'zone': openstack_properties['zone'],
                       }
            }

    volume_id = helpers.create_bootable_volume(data, host)
    assert volume_id is not None

    volumes = helpers.get_resource_list_by_name('volume', host)
    assert volumes
    volume_names = [x['Name'] for x in volumes]
    assert volume_name in volume_names
    assert tmp_var.get_expected_value('volume',
                                      volume_name,
                                      'status',
                                      'available',
                                      host,
                                      retries=50)

    return volume_id


@pytest.mark.test_id('8b701dbc-7584-11e8-ba5b-fe14fb7452aa')
@pytest.mark.jira('asc-462')
def test_create_instance_from_bootable_volume(openstack_properties,
                                              create_bootable_volume,
                                              host):
    """Test to verify that a bootable volume can be created based on a
    Glance image

    Args:
        openstack_properties (dict): fixture 'openstack_properties' from
        conftest.py
        create_bootable_volume: fixture 'create_bootable_volume'
        host(testinfra.host.Host): Testinfra host fixture
    """

    network_id = helpers.get_id_by_name('network',
                                        openstack_properties['network_name'],
                                        host)
    assert network_id is not None

    random_str = helpers.generate_random_string(6)
    instance_name = "test_instance_{}".format(random_str)

    cmd = ("{} openstack server create "
           " --volume {}"
           " --flavor {}"
           " --nic net-id={} {}'".format(utility_container,
                                         create_bootable_volume,
                                         openstack_properties['flavor'],
                                         network_id,
                                         instance_name)
           )

    host.run_expect([0], cmd)

    instances = helpers.get_resource_list_by_name('server', host)
    assert instances
    instance_names = [x['Name'] for x in instances]
    assert instance_name in instance_names
    assert tmp_var.get_expected_value('server',
                                      instance_name,
                                      'status',
                                      'ACTIVE',
                                      host,
                                      retries=30)
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
