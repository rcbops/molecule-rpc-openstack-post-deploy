from time import sleep
import json
import pytest_rpc.helpers as helpers


os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
          "-- bash -c '. /root/openrc ; ")
os_post = "'"
os_galera = ("lxc-attach -n $(lxc-ls -1 | grep galera | head -n 1) -- ")
line = "#######################################################################"


# TODO: move this function to pytest_RPC
def show_all_status(run_on_host):
    # Show Galera Status:
    print line
    print "# Galera Status:"
    mysql_cmd = "mysql -h localhost -e \"SHOW STATUS WHERE Variable_name " \
                "LIKE 'wsrep_clu%'\""
    print "Command: {}".format(mysql_cmd)
    cmd = "{} {}".format(os_galera, mysql_cmd)
    galera_result = run_on_host.run(cmd)
    print galera_result.stdout

    # openstack resoure List:
    list_resources = ['compute service',
                      'server',
                      'volume',
                      'volume service',
                      'image',
                      'router',
                      'network',
                      'subnet',
                      'availability zone',
                      'endpoint'
                      ]

    for resource in list_resources:
        cmd = "openstack {} list".format(resource)
        run_command(cmd, run_on_host)

    # openstack resource show :
    show_resources = ['nova',
                      'keystone',
                      'glance',
                      'heat',
                      'swift',
                      'cinder',
                      'neutron'
                      ]

    for resource in show_resources:
        cmd = "openstack service show {}".format(resource)
        run_command(cmd, run_on_host)


def run_command(cmd, run_on_host):
    print line
    print "Command: {}".format(cmd)
    cmd = "{} {} {}".format(os_pre, cmd, os_post)
    result = run_on_host.run(cmd)
    print result.stdout
    print "\n=== End of running command {} ===\n\n\n".format(cmd)


# TODO: move this modified function to pytest_RPC
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
        cmd = (". ~/openrc ; "
               "openstack {} show \'{}\' "
               "-f json".format(resource_type, resource_name))
        output = helpers.run_on_container(cmd, 'utility', run_on_host)

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
    # noinspection PyUnboundLocalVariable
    print("\ncmd = {}".format(cmd))
    # noinspection PyUnboundLocalVariable
    print("\nOutput:\n {}".format(result))
    print("\n===== End of get_expected_value logs =====")
    show_status = show_all_status(run_on_host).stdout
    print("\nOpenstack status:\n {}".format(show_status))

    return False
