# The helpers in this file were copied from pytest-rpc and altered to not be
# dependent on an RPC-O installation.

import json
from time import sleep

# TODO: Put these values into ansible facts
cli_host = 'director'
cli_openrc_path = '/home/stack/overcloudrc'

os_pre = ". {} ; openstack ".format(cli_openrc_path)


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
