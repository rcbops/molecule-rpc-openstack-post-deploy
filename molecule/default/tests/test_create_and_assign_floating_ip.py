# -*- coding: utf-8 -*-
"""ASC-240: Verify the requested glance images were uploaded

RPC 10+ manual test 10
"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest
from conftest import ping_from_mnaio


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('ab24ffbd-798b-11e8-a2b2-6c96cfdb2e43')
@pytest.mark.jira('ASC-254', 'ASC-1311')
def test_assign_floating_ip_to_instance(tiny_cirros_server):
    """Verify that a floating IP can be attached to a server instance.

    Args:
        tiny_cirros_server (openstack.compute.v2.server.Server): Create a
            'm1.tiny' server instance with a Cirros image.
    """

    assert ping_from_mnaio(tiny_cirros_server.accessIPv4, retries=5)
