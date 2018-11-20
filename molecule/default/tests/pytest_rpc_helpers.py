# The helpers in this file were copied from pytest-rpc and altered to not be
# dependent on an RPC-O installation.

import json
import uuid
from time import sleep

# TODO: Put these values into ansible facts
cli_host = 'director'
cli_openrc_path = '/home/stack/overcloudrc'

cli_pre = ". {} ; ".format(cli_openrc_path)
os_pre = "{} openstack ".format(cli_pre)


def get_expected_value(resource_type,
                       resource_name,
                       key,
                       expected_value,
                       run_on_host,
                       retries=10,
                       case_insensitive=True):
    """Getting an expected status after retries

    Args:
        resource_type (str): The OpenStack object type to query for.
        resource_name (str): The name of the OpenStack object instance to query
            for.
        key (str): The OpenStack object instance parameter to check against.
        expected_value (str): The expected value for the given key.
        run_on_host (testinfra.Host): Testinfra host object to execute the
            action on.
        retries (int): The maximum number of retry attempts.
        case_insensitive (bool): Flag for controlling whether to match case
            sensitive or not for the 'expected_value'.

    Returns:
        bool: Whether the expected value was found or not.
    """

    for i in range(0, retries):
        sleep(6)
        cmd = ("{} {} show \'{}\' "
               "-f json".format(os_pre, resource_type, resource_name))
        output = run_on_host.run(cmd)

        try:
            result = json.loads(output.stdout)
        except ValueError as e:
            result = str(e)
            continue

        if key in result:
            if result[key] == expected_value:
                return True
            elif result[key].lower() == expected_value and case_insensitive:
                return True
            else:
                continue
        else:
            print("\n Key not found: {}\n".format(key))
            break

    # Printing out logs if failed
    print("\n===== Debug: get_expected_value logs =====")
    print("\ncmd = {}".format(cmd))
    print("\nOutput:\n {}".format(result))
    print("\n===== End of get_expected_value logs =====")

    return False


def get_resource_list_by_name(name, run_on_host):
    """Get a list of OpenStack object instances of given type.

    Args:
        name (str): The OpenStack object type to query for.
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.

    Returns:
        list of dict: OpenStack object instances parsed from JSON
    """

    cmd = "{} {} list -f json".format(os_pre, name)
    output = run_on_host.run(cmd)
    try:
        result = json.loads(output.stdout)
    except ValueError:
        result = []
    return result


def get_id_by_name(service_type, service_name, run_on_host):
    """Get the id associated with name

    Args:
        service_type (str): The OpenStack object type to query for.
        service_name (str): The name of the OpenStack object instance to query
                            for.
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.

    Returns:
        str: Id of Openstack object instance. None if result not found.
    """

    resources = get_resource_list_by_name(service_type, run_on_host)
    if not resources:
        return

    try:
        matches = [x for x in resources if x['Name'] == service_name]
    except (KeyError, TypeError):
        try:
            matches = [x for x in resources if x['Display Name'] == service_name]
        except (KeyError, TypeError):
            return

    if not matches:
        return

    result = matches[0]

    if 'ID' in result.keys():
        return result['ID']
    else:
        return


def create_floating_ip(network_name, run_on_host):
    """Create floating IP on a network

    Args:
        network_name (str): The name of the OpenStack network object on which the floating IP is created.
        run_on_host (testinfra.Host): Testinfra host object to execute the action on.

    Returns:
        str: The newly created floating ip name

    Raises:
        AssertionError: If operation is unsuccessful.
    """

    network_id = get_id_by_name('network', network_name, run_on_host)
    assert network_id is not None

    cmd = "{} floating ip create -f json {}".format(os_pre, network_id)
    output = run_on_host.run(cmd)

    assert (output.rc == 0)

    try:
        result = json.loads(output.stdout)
    except ValueError:
        result = output.stdout

    assert type(result) is dict
    key = 'floating_ip_address'
    assert key in result.keys()

    return result[key]


def create_bootable_volume(data, run_on_host):
    """Create a bootable volume using a json file

    Args:
        data (dict): Dictionary in the following format:
                     { 'volume': { 'size': '',
                                   'imageref': '',
                                   'name': '',
                                   'zone': '',
                                 }
                     }
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.

    Returns:
        str: The id of the created resource

    Raises:
        AssertionError: If failed to create the resource
    """

    cmd = ("{} volume create "
           "-f json "
           "--size {} "
           "--image {} "
           "--availability-zone {} "
           "--bootable {}".format(os_pre,
                                  data['volume']['size'],
                                  data['volume']['imageref'],
                                  data['volume']['zone'],
                                  data['volume']['name']))

    output = run_on_host.run(cmd)

    try:
        result = json.loads(output.stdout)
    except ValueError:
        result = output.stdout

    assert type(result) is dict
    assert 'id' in result

    return result['id']


def delete_volume(volume_name, run_on_host, addl_flags=''):
    """Delete OpenStack volume

    Args:
        volume_name (str): OpenStack volume identifier (name or id).
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      action on.

    Raises:
        AssertionError: If operation unsuccessful.
    """

    delete_it('volume', volume_name, run_on_host, addl_flags=addl_flags)


def delete_it(service_type, service_name, run_on_host, addl_flags=''):
    """Delete an OpenStack object

    Args:
        service_type (str): The OpenStack object type to query for.
        service_name (str): The name of the OpenStack object to query for.
        run_on_host (testinfra.Host): Testinfra host object to execute the action on.
        addl_flags (str): Additional flags to pass to the openstack command

    Raises:
        AssertionError: If operation is unsuccessful.
    """

    service_id = get_id_by_name(service_type, service_name, run_on_host)
    cmd = ("{} {} delete "
           "{} "
           "{}".format(os_pre, service_type, addl_flags, service_id))

    assert run_on_host.run(cmd).rc == 0
    assert (resource_not_in_the_list(service_type, service_name, run_on_host))


def resource_not_in_the_list(service_type, service_name, run_on_host):
    """ Verify if the resource in NOT in the list

    Args:
        service_type (str): The OpenStack object type to query for.
        service_name (str): The name of the OpenStack object to query for.
        run_on_host (testinfra.Host): Testinfra host object to execute the action on.

    Returns:
        bool: True if the resource is NOT in the list, False if the resource is in the list
    """

    return _resource_in_list(service_type, service_name, False, run_on_host)


def _resource_in_list(service_type, service_name, expected_resource, run_on_host, retries=10):
    """Verify if a volume/server/image is existing

    Args:
        service_type (str): The OpenStack object type to query for.
        service_name (str): The name of the OpenStack object to query for.
        expected_resource (bool): Whether or not the resource is expected in the list
        run_on_host (testinfra.Host): Testinfra host object to execute the action on.
        retries (int): The maximum number of retry attempts.

    Returns:
        bool: Whether the expected resource was found or not.
    """

    SLEEP = 2

    for i in range(0, retries):

        res_id = get_id_by_name(service_type, service_name, run_on_host)

        # Expecting that a resource IS in the list, for example after creating
        # a resource, it is not shown in the list until several seconds later,
        # retry every SLEEP seconds until reaching max retries (default = 10)
        # to ensure the expected resource seen in the list.
        if expected_resource:
            if res_id:
                return True
            else:
                sleep(SLEEP)

        # Expecting that a resource is NOT in the list, for example after
        # deleting a resource, it is STILL shown in the list until several
        # seconds later, retry every SLEEP seconds until reaching max retries
        # (default = 10) to ensure the resource is removed from the list
        else:
            if not res_id:
                return True
            else:
                sleep(SLEEP)
    return False


def generate_random_string(string_length=10):
    """Generate a random string of specified length string_length.

    Args:
        string_length (int): Size of string to generate.

    Returns:
        str: Random string of specified length (maximum of 32 characters)
    """
    random_str = str(uuid.uuid4())
    random_str = random_str.upper()
    random_str = random_str.replace("-", "")
    return random_str[0:string_length]  # Return the random_str string.


def create_instance(data, run_on_host):
    """Create an instance from source (a glance image or a snapshot)

    Args:
        data (dict): Dictionary in the following format:
                    data = {
                        "instance_name": 'instance_name',
                        "from_source": 'image',
                        "source_name": 'image_name',
                        "flavor": 'flavor',
                        "network_name": 'network',
                    }
        run_on_host (testinfra.host.Host): A hostname where the command is being executed.

    Returns:
        str: The id of the created resource

    Raises:
        AssertionError: If failed to create the resource

    Example:
    `openstack server create --image <image_id> flavor <flavor> --nic <net-id=network_id> server/instance_name`
    `openstack server create --snapshot <snapshot_id> flavor <flavor> --nic <net-id=network_id> server/instance_name`
    """
    source_id = get_id_by_name(data['from_source'], data['source_name'], run_on_host)
    network_id = get_id_by_name('network', data['network_name'], run_on_host)

    cmd = ("{} server create "
           "-f json "
           "--{} {} "
           "--flavor {} "
           "--nic net-id={} {}".format(os_pre, data['from_source'],
                                       source_id, data['flavor'],
                                       network_id,
                                       data['instance_name']))

    output = run_on_host.run(cmd)

    try:
        result = json.loads(output.stdout)
    except ValueError:
        result = output.stdout

    assert type(result) is dict
    assert 'id' in result

    return result['id']


def create_snapshot_from_instance(snapshot_name, instance_name, run_on_host):
    """Create snapshot on an instance

    Args:
        snapshot_name (str): The name of the OpenStack snapshot to be created.
        instance_name (str): The name of the OpenStack instance from which the snapshot is created.
        run_on_host (testinfra.Host): Testinfra host object to execute the action on.

    Returns:
        str: The id of the created resource

    Raises:
        AssertionError: If failed to create the resource
    """

    instance_id = get_id_by_name('server', instance_name, run_on_host)
    cmd = ("{} server image create "
           "-f json "
           "--name {} {}".format(os_pre, snapshot_name, instance_id))

    output = run_on_host.run(cmd)

    try:
        result = json.loads(output.stdout)
    except ValueError:
        result = output.stdout

    assert type(result) is dict
    assert 'id' in result

    return result['id']


def parse_table(ascii_table):
    """Parse an OpenStack ascii table

    Args:
        ascii_table (str): OpenStack ascii table.

    Returns:
        list of str: Column headers from table.
        list of str: Rows from table.
    """
    header = []
    data = []
    for line in filter(None, ascii_table.split('\n')):
        if '-+-' in line:
            continue
        if not header:
            header = list(filter(lambda x: x != '|', line.split()))
            continue
        data_row = []
        splitted_line = list(filter(lambda x: x != '|', line.split()))
        for i in range(len(splitted_line)):
            data_row.append(splitted_line[i])
        while len(data_row) < len(header):
            data_row.append('')
        data.append(data_row)
    return header, data
