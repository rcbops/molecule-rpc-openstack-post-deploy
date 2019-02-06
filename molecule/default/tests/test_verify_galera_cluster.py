# -*- coding: utf-8 -*-

# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import testinfra.utils.ansible_runner


# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')

galera_container = "lxc-attach -n $(lxc-ls -1 | grep galera | head -n 1) -- "


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('2e1fa570-6827-11e8-a634-9cdc71d6c128')
@pytest.mark.jira('asc-233', 'asc-1084', 'asc-1330')
def test_verify_galera_cluster(host):
    """Verify the galera cluster is up and running

    Args:
        host(testinfra.host.Host): Testinfra host fixture.
    """

    mysql_cmd = "mysql -h localhost -e \"show status " \
                "where Variable_name like 'wsrep_clu%' " \
                "or Variable_name like 'wsrep_local_state%';\""

    cmd = "{} {}".format(galera_container, mysql_cmd)

    output = host.run(cmd)
    verify_items = ['wsrep_cluster_conf_id',
                    'wsrep_cluster_size',
                    'wsrep_cluster_state_uuid',
                    'wsrep_cluster_status',
                    'wsrep_local_state_uuid']

    for item in verify_items:
        assert item in output.stdout
