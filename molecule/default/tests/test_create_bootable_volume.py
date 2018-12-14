import pytest_rpc.helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner
import utils as tmp_var

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


@pytest.mark.test_id('3c469966-4fcb-11e8-a604-6a0003552100')
@pytest.mark.jira('asc-258')
def test_create_bootable_volume(os_props, host):
    """Test to verify that a bootable volume can be created based on a
    Glance image

    Args:
        os_props (dict): This fixture returns a dictionary of OpenStack facts
            and variables from Ansible which can be used to manipulate
            OpenStack objects.
        host(testinfra.host.Host): Testinfra host fixture.
    """
    image_id = helpers.get_id_by_name(
        'image',
        os_props['osa_ops_resources']['image_name'],
        host
    )
    assert image_id is not None

    random_str = helpers.generate_random_string(7)
    volume_name = "test_volume_{}".format(random_str)

    data = {'volume': {'size': '12',
                       'imageref': image_id,
                       'name': volume_name,
                       'zone': os_props['zone'],
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
