# -*- coding: utf-8 -*-
""" ASC-187: Verify nova_force_config_drive setting is disabled
    RPC 10+ manual test 1
"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import re
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('43e5ed40-4335-11e8-a701-6a00035510c0')
@pytest.mark.jira('asc-187')
def test_verify_nova_force_config_drive_is_disabled(host):
    """Test to verify that force config_drive is disabled in checked_host.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.

    Description:
        This test is to verify that the force config_drive must be disabled
        in the checked host. It means the `config_files` must satisfy
        the conditions below:
        1. The 'nova_force_config_drive' is not found in the `config_file`.
        2. In case `config_file` has 'nova_force_config_drive', it must be
        set to 'False'|'false', but not 'True'|'true' nor 'None'|'none'
    """

    conf_files = ['/etc/openstack_deploy/user_variables.yml',
                  '/etc/ansible/roles/os_nova/defaults/main.yml']
    for conf_file in conf_files:
        # Fail the test if the config files are not existing:
        assert host.file(conf_file).exists

        if host.file(conf_file).contains('nova_force_config_drive'):
            cmd = "grep nova_force_config_drive " + conf_file
            output = host.check_output(cmd)
            # Verify the 'nova_force_config_drive' is set to be False
            assert (re.search(r'nova_force_config_drive:\s+[F|f]alse', output))
