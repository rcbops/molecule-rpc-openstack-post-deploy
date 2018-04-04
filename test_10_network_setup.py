import os
import re
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('compute-infra_hosts')[:1]

PLAYBOOK_DIR = "/opt/openstack-ansible-ops/multi-node-aio-xenial-ansible/playbooks/"
PLAYBOOK_SERVICE_YML = PLAYBOOK_DIR + "openstack-service-setup.yml"
DYNAMIC_INV = "/opt/openstack-ansible/playbooks/inventory/dynamic_inventory.py"


@pytest.mark.jira('asc-344')
def test_setup_network(host):
    """Create network and subnet"""

    # Test to create network and subnet
    cmd = "export ANSIBLE_HOST_KEY_CHECKING=False ; " + "cd " + PLAYBOOK_DIR + " ; ansible-playbook -i " \
           + DYNAMIC_INV + " --tags create_networks " + PLAYBOOK_SERVICE_YML
    output = host.run(cmd)
    print ("stdout:\n" + output.stdout)

    # Verify ansible playbook run successfully to create network and subnet
    assert not ('failed=1' in output.stdout)
    assert ("GATEWAY_NET" in output.stdout)
    assert ("PRIVATE_NET" in output.stdout)
    assert ("GATEWAY_NET_SUBNET" in output.stdout)
    assert ("PRIVATE_NET_SUBNET" in output.stdout)
