import os
import testinfra.utils.ansible_runner
import pytest
import pytest_rpc.helpers as helpers

"""ASC-299: Verify swift endpoint status

See RPC 10+ Post-Deployment QC process document
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


@pytest.mark.test_id('d7fc4b42-432a-11e8-9ef9-6a00035510c0')
@pytest.mark.jira('ASC-299')
def test_verify_swift_stat(host):
    """Verify the swift endpoint status."""

    result = helpers.run_on_swift('swift stat -v', host)

    assert 'Account: AUTH_' in result.stdout
    assert 'X-Trans-Id: tx' in result.stdout
