# -*- coding: utf-8 -*-
"""ASC-298: Verify all swift rings are mounted using swift-recon tool

See RPC 10+ Post-Deployment QC process document
"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import pytest_rpc.helpers as helpers
import testinfra.utils.ansible_runner


# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('4b0691b8-8b9e-11e8-8fb0-a860b622fd2c')
@pytest.mark.jira('ASC-298', 'ASC-1325')
def test_verify_swift_ring_mounted(host):
    """Verify all swift rings are mounted using swift-recon.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    result = helpers.run_on_swift('swift-recon --unmounted', host)
    swift_data = helpers.parse_swift_recon(result.stdout)

    assert len(swift_data) > 1, "swift-recon did not return expected data"

    # assert no output found for unmounted drives
    assert len(swift_data[1]) == 1, ('Unmounted swift drives found:\n{}'
                                     .format('\n'.join(swift_data[1])))
