# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import pytest
import openstack
import pytest_rpc.helpers as helpers
from time import sleep
from warnings import warn


# ==============================================================================
# Helpers
# ==============================================================================
# TODO: Need to move this to 'pytest-rpc' eventually. (ASC-1412)
def expect_os_property(os_api_conn,
                       os_service,
                       os_object,
                       os_prop_name,
                       expected_value,
                       retries=10,
                       show_warnings=True,
                       case_insensitive=True,
                       only_extended_props=False):
    """Test whether an OpenStack object property matches an expected value.

    Note: this function uses an exponential back-off for retries which means the
    more retries specified the longer the wait between each retry. The total
    wait time is on the fibonacci sequence. (https://bit.ly/1ee23o9)

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        os_service (str): The service to inspect for object state.
            (e.g. 'server', 'network', 'floating_ip')
        os_object (munch.Munch): The OpenStack object to inspect. (Note: this
            can also OpenStack resource types: https://bit.ly/2R7yjbi)
        os_prop_name (str): The name of the OpenStack object property to
            inspect.
        expected_value (str): The expected value for the given property.
        retries (int): The maximum number of retry attempts.
        show_warnings (bool): Flag for displaying warnings while attempting
            validate properties.(VERY NOISY!)
        case_insensitive (bool): Flag for controlling whether to match case
            sensitive or not for the 'expected_value'.
        only_extended_props (bool): Flag for forcing searching of ONLY extended
            OpenStack properties on the given OpenStack object.

    Returns:
        bool: Whether the property matched the expected value.

    Raises:
        RuntimeError: Invalid service specified.
        RuntimeError: The property was not found on the given object.
    """

    try:
        get_service_method = getattr(os_api_conn, "get_{}".format(os_service))
    except AttributeError:
        raise RuntimeError("Invalid '{}' service specified!".format(os_service))

    for attempt in range(1, retries + 1):
        result = get_service_method(os_object.id)

        # Search direct properties and extended properties.
        if not only_extended_props and os_prop_name in result:
            actual_value = str(result[os_prop_name])
        elif 'properties' in result and os_prop_name in result['properties']:
            actual_value = str(result['properties'][os_prop_name])
        else:
            raise RuntimeError("The '{}' property was not found on the "
                               "given object!".format(os_prop_name))

        if actual_value == expected_value:
            return True
        elif actual_value.lower() == expected_value and case_insensitive:
            return True
        else:
            if show_warnings:
                warning_message = (
                    "Validation attempt: #{}\n"
                    "Object ID: '{}'\n"
                    "Property name: '{}'\n"
                    "Expected value: '{}'\n"
                    "Actual value: '{}'".format(
                        attempt,
                        os_object.id,
                        os_prop_name,
                        expected_value,
                        actual_value
                    )
                )
                warn(UserWarning(warning_message))

        sleep(attempt)

    return False


# ==============================================================================
# Fixtures
# ==============================================================================
# TODO: these fixtures should be enhanced and moved to 'pytest-rpc'. (ASC-1253)
@pytest.fixture
def openstack_properties():
    """This fixture returns a dictionary of OpenStack facts and variables from
    Ansible which can be used to manipulate OpenStack objects. (i.e. create
    server instances)

    Returns:
        dict: a static dictionary of data about OpenStack.
    """

    # TODO: Duplicate properties is tech debt caused by a refactor. (ASC-1410)
    os_properties = {
        'image_name': 'Cirros-0.3.5',
        'cirros_image': 'Cirros-0.3.5',
        'network_name': 'GATEWAY_NET',
        'private_net': 'PRIVATE_NET',
        'test_network': 'TEST-VXLAN',
        'flavor': 'm1.tiny',
        'tiny_flavor': 'm1.tiny',
        'zone': 'nova',
        'key_name': 'rpc_support',
        'security_group': 'rpc-support'
    }

    return os_properties


@pytest.fixture
def os_api_conn():
    """Provide an authorized API connection to the 'default' cloud on the
    OpenStack infrastructure.

    Returns:
        openstack.connection.Connection: https://bit.ly/2LqgiiT
    """

    return openstack.connect(cloud='default')


@pytest.fixture
def create_server(os_api_conn, openstack_properties):
    """Create OpenStack server instances with automatic teardown after each
    test.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        openstack_properties(dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.

    Returns:
        def: A factory function object.

    Raises:
        openstack.connection.exceptions.OpenStackCloudException: A server could
            not be deleted in teardown.
        UserWarning: Server not present when clean-up attempted in teardown.
    """

    servers = []  # Track inventory of server instances for teardown.

    def _factory(name,
                 image,
                 flavor,
                 network,
                 key_name,
                 security_groups,
                 retries=10,
                 timeout=600,
                 show_warnings=True,
                 skip_teardown=False):
        """Create an OpenStack instance.

        Args:
            image (openstack.image.v2.image.Image): The image property as
                returned from server. (https://bit.ly/2UXESvW)
                Name or OpenStack ID is also acceptable.
            flavor (openstack.compute.v2.flavor.Flavor): The flavor property as
                returned from server. (https://bit.ly/2Lxwqzv)
                Name or OpenStack ID is also acceptable.
            network (openstack.network.v2.network.Network): Network dict or name
                or ID to attach the server to. Mutually exclusive with the nics
                parameter. Can also be be a list of network names or IDs or
                network dicts. (https://bit.ly/2A104IL)
            key_name (str): The name of an associated keypair.
            security_groups(list): A list of security group names.
            retries (int): The maximum number of validation retry attempts.
            timeout (int): Seconds to wait, defaults to 600.
            show_warnings (bool): Flag for displaying warnings while attempting
                validate server.(VERY NOISY!)
            skip_teardown (bool): Skip automatic teardown for this server
                instance.

        Returns:
            openstack.compute.v2.server.Server: FYI, this class is not visible
                to the outside user until it gets instantiated.
                (https://bit.ly/2rMu7iQ)

        Raises:
            openstack.connection.exceptions.OpenStackCloudException: The server
                could not be created for some reason.

        Example:
            >>> conn = openstack.connect(cloud='default')
            >>> image = conn.compute.find_image('test_image')
            >>> flavor = conn.compute.find_flavor('test_flavor')
            >>> network = conn.network.find_network('test_network')
            >>> key_pair_name = 'test_keypair'
            >>> security_groups = ['test-security-group']
            >>>
            >>> server = _factory(name='test_server',
            >>>                   image=image,
            >>>                   flavor=flavor,
            >>>                   network=network,
            >>>                   key_name=key_pair_name,
            >>>                   security_groups=security_groups)

            See https://bit.ly/2EDWA2S for more details.
        """

        temp_server = os_api_conn.create_server(
            wait=True,
            name=name,
            image=image,
            flavor=flavor,
            network=network,
            timeout=timeout,
            key_name=key_name,
            security_groups=security_groups
        )

        shared_args = {'retries': retries,
                       'os_object': temp_server,
                       'os_service': 'server',
                       'os_api_conn': os_api_conn,
                       'show_warnings': show_warnings}

        # Verify that the server is on and running.
        assert expect_os_property(os_prop_name='status',
                                  expected_value='ACTIVE',
                                  **shared_args)

        assert expect_os_property(os_prop_name='power_state',
                                  expected_value='1',
                                  only_extended_props=True,
                                  **shared_args)

        assert expect_os_property(os_prop_name='vm_state',
                                  expected_value='active',
                                  only_extended_props=True,
                                  **shared_args)

        if not skip_teardown:
            servers.append(temp_server)  # Add server to inventory for teardown.

        return temp_server

    yield _factory

    # Teardown
    for server in servers:
        if not os_api_conn.delete_server(name_or_id=server, wait=True):
            warn(UserWarning("Attempted to delete non-existent server!"
                             " ID: {}".format(server.id)))


@pytest.fixture
def tiny_cirros_server(create_server, openstack_properties):
    """Create an 'm1.tiny' server instance with a Cirros image.

    Args:
        create_server (def): A factory function for generating servers.
        openstack_properties(dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.

    Returns:
        openstack.compute.v2.server.Server: FYI, this class is not visible
            to the outside user until it gets instantiated.
            (https://bit.ly/2rMu7iQ)
    """

    return create_server(
        name="cirros_{}".format(helpers.generate_random_string()),
        image=openstack_properties['cirros_image'],
        flavor=openstack_properties['tiny_flavor'],
        network=openstack_properties['test_network'],
        key_name=openstack_properties['key_name'],
        show_warnings=False,
        security_groups=[openstack_properties['security_group']]
    )
