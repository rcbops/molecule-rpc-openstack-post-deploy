import os
import pytest
import testinfra.utils.ansible_runner


"""ASC-255: Verify no more than 1 RabbitMQ channels per RabbitMQ connection

RPC 10+ manual test 13
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

# attach the rabbitMQ container:
attach_rabbitmq_container = "lxc-attach -n `lxc-ls -1 | grep rabbit | head -n 1` -- "


@pytest.mark.test_id('43e5eed1-4335-11e8-bff9-6a00035510c0')
@pytest.mark.jira('asc-255')
def test_verify_rabbitmq_channel_per_connection(host):
    """Verify the glance images created by:
    https://github.com/openstack/openstack-ansible-ops/blob/master/multi-node-aio/playbooks/vars/openstack-service-config.yml
    """
    cmd = attach_rabbitmq_container + "rabbitmqctl list_connections name channels | sort -nk 4 | tail -n1 | awk \'{print $4}\'"
    output = host.run(cmd)
    assert (output.stdout == '1')
