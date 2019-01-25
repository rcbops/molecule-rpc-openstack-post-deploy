# -*- coding: utf-8 -*-
"""ASC-241: Per network, spin up an instance on each hypervisor, perform
external ping, and tear-down."""
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import testinfra.utils.ansible_runner
from time import sleep

# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture
def neutron_cmd(host):
    """Discover the optimal connection path to neutron agents and then provide
    a helper factory for executing commands on the given neutron agent.

    Args:
        host(testinfra.host.Host): Testinfra host fixture.

    Returns:
        def: A factory function object.

    Raises:
        AssertionError: Failure to discover a neutron agent.
    """

    # neutron_agent connection lookup
    na_list = testinfra.utils.ansible_runner.AnsibleRunner(
        os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('neutron_agent')
    hostname = host.check_output('hostname')

    na_list = [x for x in na_list if hostname in x]
    neutron_agent = next(iter(na_list), None)

    # Verify an agent was found
    assert neutron_agent

    # Set neutron agent command prefix
    if 'container' in neutron_agent:
        # lxc
        na_pre = "lxc-attach -n {} -- bash -c ".format(neutron_agent)
    else:
        # ssh
        na_pre = ("ssh -o StrictHostKeyChecking=no "
                  "-o UserKnownHostsFile=/dev/null {} ").format(neutron_agent)

    def _factory(cmd):
        """Execute a command on the given neutron agent.

        Args:
            cmd (str): Command to execute on given neutron agent.

        Returns:
            bool: True if command executes and returns an acceptable exit code,
                otherwise False.
        """

        return host.run("{} '{}'".format(na_pre, cmd))

    yield _factory


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('c3002bde-59f1-11e8-be3b-6c96cfdb252f')
@pytest.mark.jira('ASC-241', 'ASC-883', 'ASC-789', 'RI-417', 'ASC-1319')
def test_hypervisor_vms(neutron_cmd,
                        os_api_conn,
                        create_server,
                        openstack_properties):
    """ASC-241: Per network, spin up an instance on each hypervisor, perform
    external ping, and tear-down

    Args:
        neutron_cmd (def): Test fixture helper for executing commands on neutron
            agents.
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        create_server (def): A factory function for generating servers.
        openstack_properties(dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    # Init
    res = ''
    server_list = []

    # Get list of internal networks
    testable_networks = os_api_conn.search_networks(
        filters={'router:external': False}
    )

    if not testable_networks:
        pytest.skip("No testable networks found!")

    # Get list of compute availability zone names
    # noinspection PyUnresolvedReferences
    zones = [zone.name for zone in os_api_conn.compute.availability_zones()]

    # Iterate over internal networks
    for network in testable_networks:
        # Create server per network per availability zone
        for zone in zones:
            server_list.append(create_server(
                image=openstack_properties['cirros_image'],
                flavor=openstack_properties['tiny_flavor'],
                network=network['name'],
                auto_ip=False,
                key_name=openstack_properties['key_name'],
                security_groups=[],
                availability_zone=zone,
                skip_teardown=True
            ))

    # Validate that at least one server was created
    assert server_list

    for server in server_list:
        network_name = server.addresses.keys()[0]
        network_id = os_api_conn.get_network(network_name).id
        server_ip = server.addresses[network_name][0]['addr']
        gateway_id = os_api_conn.get_network(network_name).subnets[0]

        # Confirm SSH port access
        cmd = "ip netns exec qdhcp-{} nc -w1 {} 22".format(network_id,
                                                           server_ip)
        for attempt in range(60):
            res = neutron_cmd(cmd)
            try:
                assert 'SSH' in res.stdout
            except AssertionError:
                sleep(10)
            else:
                break
        else:
            assert 'SSH' in res.stdout

        if os_api_conn.get_subnet(gateway_id).gateway_ip:
            ssh = ("ssh -o StrictHostKeyChecking=no -o "
                   "UserKnownHostsFile=/dev/null "
                   "-i ~/.ssh/rpc_support cirros@{}").format(server_ip)

            # ping out
            cmd = ("ip netns exec qdhcp-{} {} "
                   "ping -c1 -w2 8.8.8.8").format(network_id, ssh)
            assert neutron_cmd(cmd).rc == 0
