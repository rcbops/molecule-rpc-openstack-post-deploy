import json
import uuid
import utils
from time import sleep

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


def create_bootable_volume(data, run_on_host):
    """Create a bootable volume using a json file"""

    volume_size = data['volume']['size']
    imageRef = data['volume']['imageRef']
    volume_name = data['volume']['name']
    zone = data['volume']['zone']

    cmd = "{} openstack volume create --size {} --image {} --availability-zone {} --bootable {}'".format(utility_container, volume_size, imageRef, zone, volume_name)
    run_on_host.run_expect([0], cmd)


def openstack_name_list(name, run_on_host):
    """Verify if a volume is existing"""
    cmd = "{} openstack {} list'".format(utility_container, name)
    output = run_on_host.run(cmd)
    return output.stdout


def delete_volume(volume_name, run_on_host):
    """Delete volume"""
    volume_id = utils.get_id_by_name('volume', volume_name, run_on_host)
    cmd = "{} openstack volume delete --purge {}'".format(utility_container, volume_id)
    output = run_on_host.run(cmd)
    assert volume_name not in output.stdout


def parse_table(ascii_table):
    header = []
    data = []
    for line in filter(None, ascii_table.split('\n')):
        if '-+-' in line:
            continue
        if not header:
            header = filter(lambda x: x != '|', line.split())
            continue
        data.append([''] * len(header))
        splitted_line = filter(lambda x: x != '|', line.split())
        for i in range(len(splitted_line)):
            data[-1][i] = splitted_line[i]
    return header, data


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


def delete_instance(instance_name, run_on_host):
    """Delete instance"""
    instance_id = utils.get_id_by_name('server', instance_name, run_on_host)
    cmd = "{} openstack server delete {}'".format(utility_container, instance_id)
    output = run_on_host.run(cmd)
    assert instance_name not in output.stdout
