import os
import re

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('compute-infra_hosts')

pre_cmd = "sudo bash -c \"source /root/openrc; "
conf_files = ['/etc/openstack_deploy/user_variables.yml,' \
              '/etc/ansible/roles/os_nova/defaults/main.yml']


def verify_nova_force_config_drive_is_disabled(host):
    for searched_file in conf_files:
        # Check nova_force_config_drive setting in /etc/openstack_deploy/user_variables.yml
        cmd = pre_cmd + "pushd /opt/openstack-ansible; " \
                        "ansible compute_hosts -m shell -a " \
                        "'grep nova_force_config_drive'" + searched_file + "\""
        # testinfra file contain something then
        output = host.check_output(cmd)

        if output:
            # Fail test if there is 'nova_force_config_drive: True'
            assert not (re.search('nova_force_config_drive:\s+True', output))
            # Fail test if there is 'nova_force_config_drive: none'
            assert not (re.search('nova_force_config_drive:\s+none', output))
            # Verify the 'nova_force_config_drive' is set to be False
            assert (re.serch('nova_force_config_drive:\s+False', output))

    host.run('popd')
