import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


@pytest.mark.test_id('d7fc5630-432a-11e8-b9da-6a00035510c0')
@pytest.mark.jira('asc-222')
def test_cinder_service(host):
    """Test to verify that cinder service is running

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """
    cmd = "{} cinder service-list'".format(utility_container)
    output = host.run(cmd)
    assert ("cinder-volume" in output.stdout)
