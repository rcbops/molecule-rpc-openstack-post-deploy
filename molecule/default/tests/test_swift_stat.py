import os
import testinfra.utils.ansible_runner
import pytest

"""ASC-299: Verify swift endpoint status

See RPC 10+ Post-Deployment QC process document
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


# Helpers
def run_on_container(command, container, run_on_host):
    """Run the given command on the given container.

    Args:
        command (str): The bash command to run.
        container (str): The container type to run the command on.
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      wrapped command on.

    Returns:
        testinfra.CommandResult: Result of command execution.
    """

    pre_command = "lxc-attach \
                   -n $(lxc-ls -1 | grep {} | head -n 1) \
                   -- bash -c ".format(container)
    cmd = "{} '{}'".format(pre_command, command)
    return run_on_host.run(cmd)


def run_on_swift(cmd, run_on_host):
    """Run the given command on the swift container.
    Args:
        cmd (str): Command
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      wrapped command on.
    Returns:
        testinfra.CommandResult: Result of command execution.
    """

    command = (". ~/openrc ; "
               ". /openstack/venvs/swift-*/bin/activate ; "
               "{}".format(cmd))
    return run_on_container(command, 'swift', run_on_host)


@pytest.mark.test_id('d7fc4b42-432a-11e8-9ef9-6a00035510c0')
@pytest.mark.jira('ASC-299')
def test_verify_swift_stat(host):
    """Verify the swift endpoint status."""

    result = run_on_swift('swift stat -v', host)

    assert 'Account: AUTH_' in result.stdout
    assert 'X-Trans-Id: tx' in result.stdout
