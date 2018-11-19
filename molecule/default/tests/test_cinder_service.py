import pytest_rpc_helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(helpers.cli_host)


@pytest.mark.test_id('d7fc5630-432a-11e8-b9da-6a00035510c0')
@pytest.mark.jira('asc-222')
def test_cinder_service(host):
    """Test to verify that cinder service is running

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json/molecule.yml
    """
    cmd = "{} cinder service-list".format(helpers.cli_pre)
    output = host.run(cmd)
    assert ("cinder-volume" in output.stdout)
