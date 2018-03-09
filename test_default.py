import os
import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('compute-infra_hosts')


# RPC 10+ manual test 1
def test_nova_force_config_drive_is_disabled(host):
    conf_files = ['/etc/openstack_deploy/user_variables.yml',
                  '/etc/ansible/roles/os_nova/defaults/main.yml']
    for conf_file in conf_files:
        if host.file(conf_file).contains('nova_force_config_drive'):
            cmd = "grep nova_force_config_drive " + conf_file
            output = host.check_output(cmd)
            # Fail test if there is 'nova_force_config_drive: True'
            assert not (re.search('nova_force_config_drive:\s+True', output))
            # Fail test if there is 'nova_force_config_drive: none'
            assert not (re.search('nova_force_config_drive:\s+none', output))
            # Verify the 'nova_force_config_drive' is set to be False
            assert (re.search('nova_force_config_drive:\s+False', output))
