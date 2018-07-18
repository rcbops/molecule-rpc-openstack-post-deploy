import os
import testinfra.utils.ansible_runner
import pytest

"""ASC-296: Verify rings have data in them and that balance in the ring file
is less than 1.00.

See RPC 10+ Post-Deployment QC process document
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


# Helpers
def run_on_container(command, container, run_on_host):
    """Run the given command on the given container.

    Args:
        command (str): The bash command to run.
        container (str): The container type to run the command on.
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      wrapped command on.

    Returns:
        testinfra.CommandResult: Result of command execution.
    """

    pre_command = "lxc-attach \
                   -n $(lxc-ls -1 | grep {} | head -n 1) \
                   -- bash -c ".format(container)
    cmd = "{} '{}'".format(pre_command, command)
    return run_on_host.run(cmd)


def parse_swift_ring_builder(ring_builder_output):
    """Parse the supplied output into a dictionary of swift ring data.

    Args:
        ring_builder_output (str): The output from the swift-ring-builder
                                   command.

    Returns:
        dictionary: Swift ring data. Empty dictionary if parse fails.

    Example data:
        {'zones': 1.0,
         'replicas': 3.0,
         'devices': 9.0,
         'regions': 1.0,
         'dispersion': 0.0,
         'balance': 0.78,
         'partitions': 256.0}
    """

    swift_data = {}
    swift_lines = ring_builder_output.split('\n')
    matching = [s for s in swift_lines if "partitions" and "dispersion" in s]
    if matching:
        elements = [s.strip() for s in matching[0].split(',')]
        for element in elements:
            v, k = element.split(' ')
            swift_data[k] = float(v)

    return swift_data


def get_swift_ring_builder_data(ring, run_on_host):
    """Get data associated with swift-ring-builder run on given ring.

    Args:
        ring (str): The swift ring to obtain data from.
        run_on_host (testinfra.Host): Testinfra host object to execute the
                                      wrapped command on.

    Returns:
        dictionary: Swift ring data. Empty dictionary on failure.

    Example data:
        {'zones': 1.0,
         'replicas': 3.0,
         'devices': 9.0,
         'regions': 1.0,
         'dispersion': 0.0,
         'balance': 0.78,
         'partitions': 256.0}
    """

    command = ". /openstack/venvs/swift-*/bin/activate && \
               swift-ring-builder /etc/swift/{}.ring.gz".format(ring)
    res = run_on_container(command, 'swift', run_on_host)
    swift_data = parse_swift_ring_builder(res.stdout)
    return swift_data


@pytest.mark.test_id('d7fc460f-432a-11e8-bd68-6a00035510c0')
@pytest.mark.jira('ASC-296')
def test_verify_account_ring_has_data(host):
    """Verify the swift account ring data partitions are greater than zero."""

    ring = 'account'
    swift_data = get_swift_ring_builder_data(ring, host)

    assert swift_data
    assert swift_data['partitions'] > 0


@pytest.mark.test_id('c5d0e70a-8611-11e8-a8d1-6a00035510c0')
@pytest.mark.jira('ASC-296')
def test_verify_account_ring_balance(host):
    """Verify the swift account ring balance is less than 1.00."""

    ring = 'account'
    swift_data = get_swift_ring_builder_data(ring, host)

    assert swift_data
    assert swift_data['balance'] < 1


@pytest.mark.test_id('c7b7eb0c-8611-11e8-ae69-6a00035510c0')
@pytest.mark.jira('ASC-296')
def test_verify_container_ring_has_data(host):
    """Verify the swift account ring balance is less than 1.00."""

    ring = 'container'
    swift_data = get_swift_ring_builder_data(ring, host)

    assert swift_data
    assert swift_data['partitions'] > 0


@pytest.mark.test_id('c82f8178-8611-11e8-861e-6a00035510c0')
@pytest.mark.jira('ASC-296')
def test_verify_container_ring_balance(host):
    """Verify the swift account ring balance is less than 1.00."""

    ring = 'container'
    swift_data = get_swift_ring_builder_data(ring, host)

    assert swift_data
    assert swift_data['balance'] < 1


@pytest.mark.test_id('c902ba5c-8611-11e8-9b8e-6a00035510c0')
@pytest.mark.jira('ASC-296')
def test_verify_object_ring_has_data(host):
    """Verify the swift account ring balance is less than 1.00."""

    ring = 'object'
    swift_data = get_swift_ring_builder_data(ring, host)

    assert swift_data
    assert swift_data['partitions'] > 0


@pytest.mark.test_id('c999e97d-8611-11e8-a927-6a00035510c0')
@pytest.mark.jira('ASC-296')
def test_verify_object_ring_balance(host):
    """Verify the swift account ring balance is less than 1.00."""

    ring = 'object'
    swift_data = get_swift_ring_builder_data(ring, host)

    assert swift_data
    assert swift_data['balance'] < 1
