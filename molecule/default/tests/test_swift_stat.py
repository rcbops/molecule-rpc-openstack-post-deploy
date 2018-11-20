import os
import testinfra.utils.ansible_runner
import pytest
import pytest_rpc.helpers as helpers

"""ASC-299: Verify swift endpoint status

See RPC 10+ Post-Deployment QC process document
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


@pytest.mark.xfail(reason='ASC-1031 - OSP MNAIO deploys ceph not swift')
@pytest.mark.test_id('d7fc4b42-432a-11e8-9ef9-6a00035510c0')
@pytest.mark.jira('ASC-299', 'RI-519')
def test_verify_swift_stat(host):
    """Verify the swift endpoint status."""

    r = host.ansible("setup")["ansible_facts"]["ansible_local"]["system_tests"]["rpc_product_release"]
    codename, major = helpers.get_osa_version(r)

    if not major.isdigit() or major > 17:
        pytest.xfail("openrc credentials are not available on the swift proxy node past queens")

    result = helpers.run_on_swift('swift stat -v', host)

    assert 'Account: AUTH_' in result.stdout
    assert 'X-Trans-Id: tx' in result.stdout
