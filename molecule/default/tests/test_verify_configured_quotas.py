# -*- coding: utf-8 -*-
"""ASC-238: Verify the quotas have been configured properly

RPC 10+ manual test 8
"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest


# ==============================================================================
# Globals
# ==============================================================================
tenant = 'service'


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('20877692-1ab3-11e9-a6df-00059a3c7a00')
@pytest.mark.jira('ASC-238', 'ASC-1328')
@pytest.mark.test_case_with_steps()
class TestUpdateTenantQuotasUsingId(object):
    """Verify that tenant quotas can be updated using ID."""

    def test_configure_quotas(self, os_api_conn):
        """Configure tenant quotas and verify it works properly.

        Args:
            os_api_conn (openstack.connection.Connection): An authorized API
                connection to the 'default' cloud on the OpenStack
                infrastructure.
        """

        # Expect
        expect_quotas = {'instances': 9, 'cores': 8, 'ram': 32}

        # Setup
        tenant_id = os_api_conn.get_project(tenant).id
        os_api_conn.set_compute_quotas(tenant_id, **expect_quotas)

        # Test
        actual_quotas = os_api_conn.get_compute_quotas(tenant_id)

        for expect_quota in expect_quotas:
            assert actual_quotas[expect_quota] == expect_quotas[expect_quota]

    def test_update_quotas_again(self, os_api_conn):
        """Update tenant quotas again with new values and verify it works
        properly.

        Args:
            os_api_conn (openstack.connection.Connection): An authorized API
                connection to the 'default' cloud on the OpenStack
                infrastructure.
        """

        # Expect
        expect_quotas = {'instances': 18, 'cores': 16, 'ram': 64}

        # Setup
        tenant_id = os_api_conn.get_project(tenant).id
        os_api_conn.set_compute_quotas(tenant_id, **expect_quotas)

        # Test
        actual_quotas = os_api_conn.get_compute_quotas(tenant_id)

        for expect_quota in expect_quotas:
            assert actual_quotas[expect_quota] == expect_quotas[expect_quota]


@pytest.mark.test_id('20876cd8-1ab3-11e9-a6df-00059a3c7a00')
@pytest.mark.jira('ASC-238', 'ASC-1328')
@pytest.mark.test_case_with_steps()
class TestUpdateTenantQuotasUsingName(object):
    """Verify that tenant quotas can be updated using name."""

    def test_configure_quotas(self, os_api_conn):
        """Configure tenant quotas and verify it works properly.

        Args:
            os_api_conn (openstack.connection.Connection): An authorized API
                connection to the 'default' cloud on the OpenStack
                infrastructure.
        """

        # Expect
        expect_quotas = {'instances': 12, 'cores': 10, 'ram': 128}

        # Setup
        os_api_conn.set_compute_quotas(tenant, **expect_quotas)

        # Test
        actual_quotas = os_api_conn.get_compute_quotas(tenant)

        for expect_quota in expect_quotas:
            assert actual_quotas[expect_quota] == expect_quotas[expect_quota]

    def test_update_quotas_again(self, os_api_conn):
        """Update tenant quotas again with new values and verify it works
        properly.

        Args:
            os_api_conn (openstack.connection.Connection): An authorized API
                connection to the 'default' cloud on the OpenStack
                infrastructure.
        """

        # Expect
        expect_quotas = {'instances': 30, 'cores': 20, 'ram': 256}

        # Setup
        os_api_conn.set_compute_quotas(tenant, **expect_quotas)

        # Test
        actual_quotas = os_api_conn.get_compute_quotas(tenant)

        for expect_quota in expect_quotas:
            assert actual_quotas[expect_quota] == expect_quotas[expect_quota]
