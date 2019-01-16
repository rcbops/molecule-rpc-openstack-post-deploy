# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import pytest_rpc.helpers as helpers
import testinfra.utils.ansible_runner
from pprint import pformat

# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture
def backup_folder_path():
    """Path of MBU backup folder for a given host type.

    Returns:
        dict: {'host', 'container'}
    """

    return {'host': '/openstack/backup', 'container': '/var/backup'}


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('406be222-cbee-11e8-ae3a-0025227c8120')
@pytest.mark.jira('ASC-262', 'ASC-1331')
@pytest.mark.test_case_with_steps()
class TestVerifyMBUInstall(object):
    """Ensure that MBU backup paths are present which are prerequisites to
    installing the MBU service.
    """

    def test_verify_backup_folder_on_host(self, host, backup_folder_path):
        """Verify backup path on virtual/physical host.

        Args:
            host (testinfra.host.Host): Testinfra host fixture.
            backup_folder_path (dict): Path of MBU backup folder for a given
                host type.
        """

        assert host.file(backup_folder_path['host']).is_directory

    def test_verify_backup_folder_on_container(self, host, backup_folder_path):
        """Verify backup path on all container hosts.

        Args:
            host (testinfra.host.Host): Testinfra host fixture.
            backup_folder_path (dict): Path of MBU backup folder for a given
                host type.
        """

        cmd1 = "ls {}".format(backup_folder_path['host'])
        containers = host.run(cmd1).stdout.split('\n')

        # Fail the test if there is no container in the backup directory
        error_msg = "No containers found!\n{}".format(pformat(containers))
        assert len(containers) > 1, error_msg

        cmd2 = "test -d {}".format(backup_folder_path['container'])
        for container in containers:
            assert (helpers.run_on_container(cmd2, container, host))
