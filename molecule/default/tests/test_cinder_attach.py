# -*- coding: utf-8 -*-
"""ASC-157: Verify Cinder instance attachments
"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import testinfra.utils.ansible_runner
from pprint import pformat
from munch import unmunchify

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]

ssh_pre = ("ssh -o UserKnownHostsFile=/dev/null "
           "-o StrictHostKeyChecking=no -q ")


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.jira('asc-157')
@pytest.mark.test_id('01912ed1-547c-11e8-847a-6c96cfdb252f')
def test_cinder_verify_attach(os_api_conn, host):
    """Test to verify cinder volume attached to a server.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        host (testinfra.host.Host): Testinfra host fixture.
    """
    # get server details:
    list_servers = os_api_conn.list_servers()

    for server in list_servers:
        hypervisor = server['hypervisor_hostname'].split('.')[0]
        instance_name = server['instance_name']
        if len(server['os-extended-volumes:volumes_attached']) > 0:
            # Verify each attached volume
            for vol in server['os-extended-volumes:volumes_attached']:
                cmd = "{} virsh dumpxml {} | grep {}".format(ssh_pre,
                                                             hypervisor,
                                                             instance_name,
                                                             vol['id'])
                assert host.run(cmd), \
                    "On Server: '{}'\n" \
                    "No cinder volume attachment is found with command: '{}' " \
                    "executed on the hypervisor: '{}' against instance_name: " \
                    "'{}'\n" \
                    "Server's details:\n{}\n"\
                    .format(pformat(unmunchify(server['id'],
                                               cmd,
                                               hypervisor,
                                               instance_name,
                                               server)))
