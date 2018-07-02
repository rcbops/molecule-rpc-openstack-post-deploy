import json
from time import sleep
import uuid

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


def get_id_by_name(service_type, service_name, run_on_host):
    """Get the id associated with name"""
    cmd = "{} openstack {} show \'{}\' -f json'".format(utility_container, service_type, service_name)
    output = run_on_host.run(cmd)
    try:
        result = json.loads(output.stdout)
    except ValueError:
        return

    if 'id' in result:
        return result['id']
    else:
        return


def create_instance(data, run_on_host):
    """Create an instance from source (a glance image or a snapshot)
    Args:
        data (dict): a dictionary of data. A sample of data as below:
                    data_image = {
                        "instance_name": instance_name,
                        "from_source": 'image',
                        "source_name": image_name,
                        "flavor": flavor,
                        "network_name": network,
                    }
        run_on_host (testinfra.host.Host): A hostname where the command is being executed.
    Example:
    `openstack server create --image <image_id> flavor <flavor> network <network_name> server/instance_name`
    `openstack server create --snapshot <snapshot_id> flavor <flavor> network <network_name> server/instance_name`
    """
    from_source = data['from_source']
    source_id = get_id_by_name(str(data['from_source']), str(data['source_name']), run_on_host)
    flavor = data['flavor']
    network_id = get_id_by_name('network', str(data['network_name']), run_on_host)
    instance_name = data['instance_name']

    cmd = "{} openstack server create --{} {} --flavor {} --nic net-id={} {}'".format(utility_container, from_source, source_id, flavor, network_id, instance_name)

    run_on_host.run_expect([0], cmd)
    sleep(10)


def verify_asset_in_list(service_type, service_name, run_on_host):
    """Verify if a volume/server/image is existing"""
    cmd = "{} openstack {} list'".format(utility_container, service_type)
    output = run_on_host.run(cmd)
    if service_name in output.stdout:
        return True
    else:
        return False


def stop_server_instance(instance_name, run_on_host):
    instance_id = get_id_by_name('server', instance_name, run_on_host)

    cmd = "{} openstack server stop {}'".format(utility_container, instance_id)
    run_on_host.run_expect([0], cmd)


def create_snapshot_from_instance(snapshot_name, instance_name, run_on_host):
    """Create snapshot on an instance"""
    instance_id = get_id_by_name('server', instance_name, run_on_host)
    cmd = "{} openstack server image create --name {} {}'".format(utility_container, snapshot_name, instance_id)

    run_on_host.run_expect([0], cmd)
    sleep(10)


def delete_it(service_type, service_name, run_on_host):
    sleep(15)
    id = get_id_by_name(service_type, service_name, run_on_host)
    cmd = "{} openstack {} delete {}'".format(utility_container, service_type, id)
    run_on_host.run_expect([0], cmd)
    sleep(20)

    assert not verify_asset_in_list(service_type, service_name, run_on_host)


def generate_random_string(string_length=10):
    """Returns a random string of length string_length."""
    random_str = str(uuid.uuid4())
    random_str = random_str.upper()
    random_str = random_str.replace("-", "")
    return random_str[0:string_length]  # Return the random_str string.


def get_expected_value(service_type, service_name, key, expected_value, run_on_host, retries=10):
    """Getting an expected status after retries"""
    for i in range(0, retries):
        cmd = "{} openstack {} show \'{}\' -f json'".format(utility_container, service_type, service_name)
        output = run_on_host.run(cmd)
        result = json.loads(output.stdout)

        if key in result:
            if result[key] == expected_value:
                return True
            else:
                sleep(6)
        else:
            return False

    return False


def create_floating_ip(network_name, run_on_host):
    """Create floating IP and return the floating ip name """

    network_id = get_id_by_name('network', network_name, run_on_host)
    assert network_id is not None

    cmd = "{} openstack floating ip create {} -f json'".format(utility_container, network_id)
    output = run_on_host.run(cmd)

    assert (output.rc == 0)

    try:
        result = json.loads(output.stdout)
    except ValueError:
        return

    if 'name' in result:
        return result['name']
    else:
        return


def ping_ip_from_host(ip, run_on_host):
    """Verify the IP address can be pinged from host"""

    cmd = "{} ping -c1 {}'".format(utility_container, ip)
    output = run_on_host.run(cmd)

    if output.rc == 0:
        return True
    else:
        return False
