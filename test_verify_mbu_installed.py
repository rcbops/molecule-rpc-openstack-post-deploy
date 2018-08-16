import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


backup_folder_on_host = '/openstack/backup'
backup_folder_on_container = '/var/backup'


@pytest.mark.incremental
class TestVerifyMBUInstall(object):
    @pytest.mark.test_id('d7fc3e85-432a-11e8-a9a2-6a00035510c0')
    @pytest.mark.jira('asc-262')
    def test_verify_backup_folder_on_host(self, host):
        assert host.file(backup_folder_on_host).is_directory

    @pytest.mark.test_id('4a7ed621-a1a3-11e8-8948-6a0003552100')
    @pytest.mark.jira('asc-262')
    def test_verify_backup_folder_on_container(self, host):
        cmd1 = "ls {}".format(backup_folder_on_host)
        containers = host.run(cmd1).stdout.split('\n')

        # Fail the test if there is no container in the backup directory
        print containers
        assert (len(containers) > 1)

        cmd2 = "test -d {}".format(backup_folder_on_container)
        for container in containers:
            assert (self.run_on_container(cmd2, container, host))

    # Helper
    def run_on_container(self, command, container, run_on_host):
        """Run the given command on the given container.
        Args:
            command (str): The bash command to run.
            container (str): The container to run the command on.
            run_on_host (testinfra.Host): Testinfra host object to execute the
                                          wrapped command on.
        Returns:
            testinfra.CommandResult: Result of command execution.
        """

        pre_command = ("lxc-attach -n {} "
                       "-- bash -c".format(container))
        cmd = "{} '{}'".format(pre_command, command)
        output = run_on_host.run(cmd)
        assert output.rc == 0
        return output
