import os
import pytest
import testinfra.utils.ansible_runner


"""
ASC-230: Reboot the nova +log hosts and ensure configuration persistence
ASC-231: Reboot infra hosts in the sequence of infra3, infra2, and then infra1
ASC-228: Reboot all cinder hosts

RPC 10+ manual test 3:
On this test, the order of rebooting has to be:
All Nova hosts -> Log hosts -> Infra3 host -> Infra2 host -> Infra1 host -> All Cinder hosts
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('haproxy')[:1]


@pytest.mark.test_id('2e1fa570-6827-11e8-a634-9cdc71d6c128')
@pytest.mark.jira('asc-233')
@pytest.mark.skip(reason='will be implemented with ticket ASC-233')
@pytest.mark.testinfra_hosts(testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('haproxy')[:1])
def test_verify_galera_cluster(host):
    """This test will be implemented with ticket ASC-233"""
