import pytest_rpc.helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner
from time import sleep

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")

random_str = helpers.generate_random_string(6)
instance_name = "test_instance_{}".format(random_str)
image_name = 'Cirros-0.3.5'
gateway_net = 'GATEWAY_NET'
private_net = 'PRIVATE_NET'
flavor = 'm1.tiny'
floating_ip = None


@pytest.mark.test_id('a97e1202-796a-11e8-ba13-525400bd8005')
@pytest.mark.jira('asc-254')
@pytest.mark.run(order=1)
def test_create_floating_ip(host):
    """Create floating IP"""

    global floating_ip
    floating_ip = helpers.create_floating_ip(gateway_net, host)
    assert floating_ip

    # Before being assigned, the floating IP status should be 'DOWN'
    assert (helpers.get_expected_value('floating ip', floating_ip, 'status', 'DOWN', host))


@pytest.mark.test_id('ab24ffbd-798b-11e8-a2b2-6c96cfdb2e43')
@pytest.mark.jira('asc-254')
@pytest.mark.run(order=2)
def test_assign_floating_ip_to_instance(host):
    """Assign floating IP to an instance/server"""

    # Creating an instance from image
    data = {
        "instance_name": instance_name,
        "from_source": 'image',
        "source_name": image_name,
        "flavor": flavor,
        "network_name": private_net,
    }

    helpers.create_instance(data, host)

    # TODO: will find out a better way to avoid implicit sleep. 'status' is 'ACTIVE' is not enough to ensure the
    # TODO: instance is ready, there are many instance statuses that might cause the test failed.
    # TODO: run `openstack server show <instance-ID> -f json` to see all the states
    sleep(120)

    # Verify the new instance is ACTIVE and Running.
    assert (helpers.get_expected_value('server', instance_name, 'status', 'ACTIVE', host, 20))
    assert (helpers.get_expected_value('server', instance_name, 'OS-EXT-STS:power_state', 'Running', host, 20))

    assert floating_ip

    instance_id = helpers.get_id_by_name('server', instance_name, host)
    assert instance_id

    cmd = "{} openstack server add floating ip {} {}'".format(utility_container, instance_id, floating_ip)

    host.run_expect([0], cmd)

    # After being assigned, the floating IP status should be 'ACTIVE'
    assert (helpers.get_expected_value('floating ip', floating_ip, 'status', 'ACTIVE', host))

    # Ensure the IP can be pinged from infra1
    cmd = "ping -c1 {}".format(floating_ip)
    assert (host.run_expect([0], cmd))

    # Cleaning test env after testing: Delete floating IP
    helpers.delete_it('floating ip', floating_ip, host)
