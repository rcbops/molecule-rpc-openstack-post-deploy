import os
import pytest
import testinfra.utils.ansible_runner

"""
ASC-230: Reboot the nova +log hosts and ensure configuration persistence
ASC-231: Reboot infra hosts in the sequence of infra3, infra2, and then infra1
ASC-228: Reboot all cinder hosts
ASC-233: Verify Galera cluster survived after the reboot

RPC 10+ manual test 3:
On this test, the order of rebooting has to be:
All Nova hosts -> Log hosts -> Infra3 host -> Infra2 host -> Infra1 host -> All Cinder hosts
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')

galera_container = ("lxc-attach -n $(lxc-ls -1 | grep galera | head -n 1) -- ")


@pytest.mark.test_id('2e1fa570-6827-11e8-a634-9cdc71d6c128')
@pytest.mark.jira('asc-233')
def test_verify_galera_cluster(host):
    """Verify the galera cluster survived after the reboot"""

    mysql_cmd = "mysql -h localhost -e \"show status " \
                "where Variable_name like 'wsrep_clu%' " \
                "or Variable_name like 'wsrep_local_state%';\""

    cmd = "{} {}".format(galera_container, mysql_cmd)

    output = host.run(cmd)

    assert "wsrep_cluster_conf_id" in output.stdout
    assert "wsrep_cluster_size" in output.stdout
    assert "wsrep_cluster_state_uuid" in output.stdout
    assert "wsrep_cluster_status" in output.stdout
    assert "wsrep_local_state_uuid" in output.stdout
