import os
import re
import pytest
import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('compute-infra_hosts')[:1]

@pytest.mark.jira('asc-344')
def test_setup_network(host):
    """Create network and subnet"""
    # work around REO-198:
    host.run("cp /opt/openstack-ansible-ops/multi-node-aio-xenial-ansible/playbooks/openstack-service-setup.yml "
             "/opt/openstack-ansible-ops/multi-node-aio-xenial-ansible/playbooks/openstack-network-setup_reo198.yml")
    host.run("sed -i '/Create flavors of nova VMs/,/^$/d' "
             "/opt/openstack-ansible-ops/multi-node-aio-xenial-ansible/playbooks/openstack-network-setup_reo198.yml")
    output1 = host.run(
        'cat /opt/openstack-ansible-ops/multi-node-aio-xenial-ansible/playbooks/openstack-network-setup.yml')
    print ("cat openstack-network-setup.yml:" + output1.stdout)

    # Test to create network and subnet
    output2 = host.run("export ANSIBLE_HOST_KEY_CHECKING=False ; "
                       "cd /opt/openstack-ansible-ops/multi-node-aio-xenial-ansible/playbooks ; ansible-playbook -i "
                       "/opt/openstack-ansible/playbooks/inventory/dynamic_inventory.py "
                       "openstack-network-setup_reo198.yml")
    print ("stdout:\n" + output2.stdout)
    # tear down, will be removed after REO-198 is fixed
    host.run("rm -rf /opt/openstack-ansible-ops/multi-node-aio-xenial-ansible/playbooks/openstack-network-setup_reo198.yml")

    # Verify ansible playbook run successfully to create network and subnet
    assert not ('failed=1' in output2.stdout)
