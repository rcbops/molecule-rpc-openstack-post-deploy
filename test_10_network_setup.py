import os
import re
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('compute-infra_hosts')[:1]

PLAYBOOK_DIR = "/opt/openstack-ansible-ops/multi-node-aio-xenial-ansible/playbooks/"
SERVICE_YML = PLAYBOOK_DIR + "openstack-service-setup.yml"
NETWORK_TEMP = PLAYBOOK_DIR + "openstack-network-setup_reo198.yml"
DYNAMIC_INV = "/opt/openstack-ansible/playbooks/inventory/dynamic_inventory.py"


@pytest.mark.jira('asc-344')
def test_setup_network(host):
    """Create network and subnet"""
    # work around REO-198:
    cmd1 = "cp " + SERVICE_YML + " " + NETWORK_TEMP
    host.run(cmd1)

    # Remove task of creating flavors of Nova VMs
    cmd2 = "sed -i '/Create flavors of nova VMs/,/^$/d' " + NETWORK_TEMP
    host.run(cmd2)

    # Test to create network and subnet
    cmd3 = "export ANSIBLE_HOST_KEY_CHECKING=False ; " + "cd " + PLAYBOOK_DIR + " ; ansible-playbook -i " \
           + DYNAMIC_INV + " " + NETWORK_TEMP
    output = host.run(cmd3)
    print ("stdout:\n" + output.stdout)

    # tear down, will be removed after REO-198 is fixed
    cmd4 = "rm -rf " + NETWORK_TEMP
    host.run(cmd4)

    # Verify ansible playbook run successfully to create network and subnet
    assert not ('failed=1' in output.stdout)
