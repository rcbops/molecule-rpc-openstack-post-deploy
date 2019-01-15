# -*- coding: utf-8 -*-
"""ASC-157: Perform Post Deploy System validations"""
# ==============================================================================
# Imports
# ==============================================================================
import pytest


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('d7fc26a8-432a-11e8-8340-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1317')
def test_projects(os_api_conn):
    """Ensure presence of basic projects.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
    """

    project_names = [project.name for project in os_api_conn.list_projects()]

    assert 'admin' in project_names
    assert 'service' in project_names


@pytest.mark.test_id('d7fc2770-432a-11e8-8af1-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1317')
def test_users(os_api_conn):
    """Ensure presence of basic users.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
    """

    actual_user_names = [
        project.name for project in os_api_conn.list_users(
            filters={'domain': 'default'})
    ]
    expect_users = ['admin',
                    'cinder',
                    'dispersion',
                    'glance',
                    'heat',
                    'keystone',
                    'neutron',
                    'nova',
                    'swift']

    for expect_user in expect_users:
        assert expect_user in actual_user_names


@pytest.mark.test_id('d7fc2835-432a-11e8-a8a1-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1317')
def test_networks(os_api_conn):
    """Ensure presence of basic networks.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
    """

    assert len(os_api_conn.list_networks()) > 0


@pytest.mark.test_id('d7fc28f5-432a-11e8-9af3-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1317')
def test_servers(os_api_conn):
    """Ensure presence of basic nova servers.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
    """

    assert os_api_conn.list_servers()


@pytest.mark.test_id('d7fc2b45-432a-11e8-92c0-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1317')
def test_flavors(os_api_conn):
    """Ensure presence of basic nova flavors.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
    """

    assert len(os_api_conn.list_flavors()) > 0


@pytest.mark.test_id('d7fc2f02-432a-11e8-8e59-6a00035510c0')
@pytest.mark.jira('ASC-157', 'ASC-1317')
def test_image(os_api_conn):
    """Ensure presence of basic glance images.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
    """

    assert len(os_api_conn.list_images()) > 0
