import pytest_rpc_helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner
import json

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(helpers.cli_host)


@pytest.mark.test_id('ab24ffbd-798b-11e8-a2b2-6c96cfdb2e43')
@pytest.mark.jira('asc-254')
def test_assign_floating_ip_to_instance(openstack_properties, host):
    """ Assign floating IP to an instance/server

    Args:
        openstack_properties (dict): fixture 'openstack_properties' from
        conftest.py
        host(testinfra.host.Host): Testinfra host fixture.
    """

    # Creating an instance from image
    random_str = helpers.generate_random_string(6)

    cmd = ('{0} server create '
           '-f json '
           '--image {1} '
           '--flavor "{2}" '
           '--nic net-id={3} '
           '--key-name rpc_support '
           '--security-group rpc-support '
           '"{4}"').format(helpers.os_pre,
                           openstack_properties['image_name'],
                           openstack_properties['flavor'],
                           openstack_properties['private_net'],
                           "test_instance_{}".format(random_str))
    res = host.run(cmd)
    instance_id = json.loads(res.stdout)['id']

    assert helpers.get_expected_value('server',
                                      instance_id,
                                      'status',
                                      'ACTIVE',
                                      host,
                                      retries=40)
    assert helpers.get_expected_value('server',
                                      instance_id,
                                      'OS-EXT-STS:power_state',
                                      'Running',
                                      host,
                                      retries=20)
    assert helpers.get_expected_value('server',
                                      instance_id,
                                      'OS-EXT-STS:vm_state',
                                      'active', host,
                                      retries=20)

    # Creating a floating IP:
    floating_ip = helpers.create_floating_ip(
        openstack_properties['network_name'],
        host
    )

    # Assigning floating ip to a server
    cmd = ("{} server add "
           "floating ip {} {}".format(helpers.os_pre,
                                      instance_id,
                                      floating_ip)
           )
    host.run_expect([0], cmd)

    # After being assigned, the floating IP status should be 'ACTIVE'
    assert (helpers.get_expected_value('floating ip',
                                       floating_ip,
                                       'status',
                                       'ACTIVE',
                                       host)
            )

    # Ensure the IP can be pinged from infra1
    cmd = "ping -c1 {}".format(floating_ip)
    assert (host.run_expect([0], cmd))
