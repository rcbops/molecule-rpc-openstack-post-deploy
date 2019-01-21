# -*- coding: utf-8 -*-
"""ASC-296: Verify rings have data in them and that balance in the ring file
is less than 1.00.

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
@pytest.mark.test_id('d7fc4cdc-432a-11e8-a5dc-6a00035510c0')
@pytest.mark.jira('ASC-300', 'ASC-1323')
def test_verify_dispersion_populate(host):
    """Verify swift-dispersion-populate runs without error.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    result = helpers.run_on_swift('swift-dispersion-populate --no-overlap',
                                  host)
    assert result.rc == 0


@pytest.mark.test_id('d7fc4e61-432a-11e8-bcf5-6a00035510c0')
@pytest.mark.jira('ASC-300', 'ASC-1323')
def test_verify_dispersion_report(host):
    """Verify swift-dispersion-report runs without error.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    result = helpers.run_on_swift('swift-dispersion-report', host)
    assert result.rc == 0
