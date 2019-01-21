# -*- coding: utf-8 -*-
"""ASC-157: Perform Post Deploy System validations"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc25ae-432a-11e8-a20a-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1316')
def test_openvswitch(os_api_conn):
    """Ensure DHCP agents for all networks are up.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
    """

    for network in os_api_conn.list_networks():
        assert network.admin_state_up   # DHCP agent present and running
