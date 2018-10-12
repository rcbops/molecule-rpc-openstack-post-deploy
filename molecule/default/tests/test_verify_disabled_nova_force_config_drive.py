import os
import re
import pytest
import testinfra.utils.ansible_runner

################################################################
# ASC-187: Verify nova_force_config_drive setting is disabled  #
################################################################
# RPC 10+ manual test 1
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('compute-infra_hosts')[:1]


@pytest.mark.test_id('43e5ed40-4335-11e8-a701-6a00035510c0')
@pytest.mark.jira('asc-187')
def test_nova_force_config_drive_is_disabled_on_nova_compute(host):
    verify_nova_force_config_drive_is_disabled(host)


@pytest.mark.test_id('43e5ee11-4335-11e8-88a0-6a00035510c0')
@pytest.mark.jira('asc-187')
def test_nova_force_config_drive_is_disabled_on_nova_scheduler(host):
    verify_nova_force_config_drive_is_disabled(host)


def verify_nova_force_config_drive_is_disabled(checked_host):
    """Test to verify that force config_drive is disabled in checked_host.

    Args:
        checked_host(string): A hostname in dynamic_inventory.json

    Description:
        This test is to verify that the force config_drive must be disabled
        in the checked_host. It means that the `config_files` must satisfy
        the conditions below:
        1. The 'nova_force_config_drive' is not found in the `config_file`.
        2. In case `config_file` has 'nova_force_config_drive', it must be
        set to 'False'|'false', but not 'True'|'true' nor 'None'|'none'
    """

    conf_files = ['/etc/openstack_deploy/user_variables.yml',
                  '/etc/ansible/roles/os_nova/defaults/main.yml']
    for conf_file in conf_files:
        # Fail the test if the config files are not existing:
        assert checked_host.file(conf_file).exists

        if checked_host.file(conf_file).contains('nova_force_config_drive'):
            cmd = "grep nova_force_config_drive " + conf_file
            output = checked_host.check_output(cmd)
            # Verify the 'nova_force_config_drive' is set to be False
            assert (re.search('nova_force_config_drive:\s+[F|f]alse', output))
