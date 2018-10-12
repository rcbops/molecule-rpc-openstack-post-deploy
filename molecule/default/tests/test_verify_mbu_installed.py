# ======================================================================================================================
# Imports
# ======================================================================================================================
import os
import pytest
import pytest_rpc.helpers as helpers
import testinfra.utils.ansible_runner

# ======================================================================================================================
# Globals
# ======================================================================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


backup_folder_on_host = '/openstack/backup'
backup_folder_on_container = '/var/backup'


# ======================================================================================================================
# Test Cases
# ======================================================================================================================
@pytest.mark.test_id('406be222-cbee-11e8-ae3a-0025227c8120')
@pytest.mark.jira('asc-262')
@pytest.mark.test_case_with_steps()
class TestVerifyMBUInstall(object):

    def test_verify_backup_folder_on_host(self, host):
        assert host.file(backup_folder_on_host).is_directory

    def test_verify_backup_folder_on_container(self, host):
        cmd1 = "ls {}".format(backup_folder_on_host)
        containers = host.run(cmd1).stdout.split('\n')

        # Fail the test if there is no container in the backup directory
        print containers
        assert (len(containers) > 1)

        cmd2 = "test -d {}".format(backup_folder_on_container)
        for container in containers:
            assert (helpers.run_on_container(cmd2, container, host))
