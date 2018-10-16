# -*- coding: utf-8 -*-

# ======================================================================================================================
# Imports
# ======================================================================================================================
import pytest
import openstack


# ======================================================================================================================
# Fixtures
# ======================================================================================================================
@pytest.fixture
def os_api_connection():
    """Provide an authorized API connection to the 'default' cloud on the OpenStack infrastructure.

    Returns:
        openstack.connection.Connection
    """

    return openstack.connect(cloud='default')
