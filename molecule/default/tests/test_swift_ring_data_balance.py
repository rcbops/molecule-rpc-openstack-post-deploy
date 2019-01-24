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

rb_cmd_tmpl = "swift-ring-builder /etc/swift/{}.ring.gz"


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc460f-432a-11e8-bd68-6a00035510c0')
@pytest.mark.jira('ASC-296', 'ASC-1326')
def test_verify_account_ring_has_data(host):
    """Verify the swift account ring data partitions are greater than zero.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    ring = 'account'
    result = helpers.run_on_swift(rb_cmd_tmpl.format(ring), host)
    swift_data = helpers.parse_swift_ring_builder(result.stdout)

    assert swift_data
    assert swift_data['partitions'] > 0


@pytest.mark.test_id('c5d0e70a-8611-11e8-a8d1-6a00035510c0')
@pytest.mark.jira('ASC-296', 'ASC-1326')
def test_verify_account_ring_balance(host):
    """Verify the swift account ring balance is less than 1.00.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    ring = 'account'
    result = helpers.run_on_swift(rb_cmd_tmpl.format(ring), host)
    swift_data = helpers.parse_swift_ring_builder(result.stdout)

    assert swift_data
    assert swift_data['balance'] < 1


@pytest.mark.test_id('c7b7eb0c-8611-11e8-ae69-6a00035510c0')
@pytest.mark.jira('ASC-296', 'ASC-1326')
def test_verify_container_ring_has_data(host):
    """Verify the swift container ring data partitions are greater than zero.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    ring = 'container'
    result = helpers.run_on_swift(rb_cmd_tmpl.format(ring), host)
    swift_data = helpers.parse_swift_ring_builder(result.stdout)

    assert swift_data
    assert swift_data['partitions'] > 0


@pytest.mark.test_id('c82f8178-8611-11e8-861e-6a00035510c0')
@pytest.mark.jira('ASC-296', 'ASC-1326')
def test_verify_container_ring_balance(host):
    """Verify the swift container ring balance is less than 1.00.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    ring = 'container'
    result = helpers.run_on_swift(rb_cmd_tmpl.format(ring), host)
    swift_data = helpers.parse_swift_ring_builder(result.stdout)

    assert swift_data
    assert swift_data['balance'] < 1


@pytest.mark.test_id('c902ba5c-8611-11e8-9b8e-6a00035510c0')
@pytest.mark.jira('ASC-296', 'ASC-1326')
def test_verify_object_ring_has_data(host):
    """Verify the swift object ring data partitions are greater than zero.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    ring = 'object'
    result = helpers.run_on_swift(rb_cmd_tmpl.format(ring), host)
    swift_data = helpers.parse_swift_ring_builder(result.stdout)

    assert swift_data
    assert swift_data['partitions'] > 0


@pytest.mark.test_id('c999e97d-8611-11e8-a927-6a00035510c0')
@pytest.mark.jira('ASC-296', 'ASC-1326')
def test_verify_object_ring_balance(host):
    """Verify the swift object ring balance is less than 1.00.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
    """

    ring = 'object'
    result = helpers.run_on_swift(rb_cmd_tmpl.format(ring), host)
    swift_data = helpers.parse_swift_ring_builder(result.stdout)

    assert swift_data
    assert swift_data['balance'] < 1
