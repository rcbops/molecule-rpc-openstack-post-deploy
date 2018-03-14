import os
import re
import pytest
import testinfra.utils.ansible_runner

################################################################
# ASC-187: Verify nova_force_config_drive setting is disabled  #
################################################################
# RPC 10+ manual test 1
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('nova_compute')


@pytest.mark.jira('asc-187')
def test_nova_force_config_drive_is_disabled_on_nova_compute(host):
    verify_nova_force_config_drive_is_disabled(host)


@pytest.mark.jira('asc-187')
def test_nova_force_config_drive_is_disabled_on_nova_scheduler(host):
    verify_nova_force_config_drive_is_disabled(host)


def verify_nova_force_config_drive_is_disabled(checked_host):
    """Test to verify that force config_drive is disabled in checked_host.

        Args:
            checked_host(string): A hostname in dynamic_inventory.json

        Returns:
            exit_code 0:(skip test) if the config file not found in the host
            exit_code 1: Test Failed
            exit_code 0: Test Passed

        Description:
            This test is to verify:
            That the force config_drive must be disabled in the checked_host.

            Skip if the config_file is not existing in the checked_host
            Failed if 'nova_force_config_drive' is set to be 'True'
                (the force is enabled)
            Failed if 'nova_force_config_drive' is set to be 'none'
                (improperly disabled)
            Fassed if 'nova_force_config_drive' is set to be 'False'
                (properly disabled)
    """

    conf_files = ['/etc/openstack_deploy/user_variables.yml',
                  '/etc/ansible/roles/os_nova/defaults/main.yml']
    for conf_file in conf_files:
        if not checked_host.file(conf_file).exists:
            pytest.skip('file not found')
        elif checked_host.file(conf_file).exists and \
                checked_host.file(conf_file).contains(
                    'nova_force_config_drive'):

            cmd = "grep nova_force_config_drive " + conf_file
            output = checked_host.check_output(cmd)
            # Fail test if there is 'nova_force_config_drive: True'
            assert not (re.search('nova_force_config_drive:\s+True', output))
            # Fail test if there is 'nova_force_config_drive: none'
            assert not (re.search('nova_force_config_drive:\s+none', output))
            # Verify the 'nova_force_config_drive' is set to be False
            assert (re.search('nova_force_config_drive:\s+False', output))
