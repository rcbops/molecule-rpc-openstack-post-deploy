# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import testinfra.utils.ansible_runner


# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


# ==============================================================================
# Helpers
# ==============================================================================
def gen_dict_extract(key, var):
    """Produce a generator that can iterate over all found values for a given
    key in a given dictionary

    Args:
        key(str): key to lookup
        var(dict): dictionary to recursively search

    Returns: generator
    """

    if hasattr(var, 'iteritems'):
        for k, v in var.iteritems():
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d):
                        yield result


def get_osa_version(branch):
    """Get OpenStack version (code_name, major_version)

    This data is based on the git branch of the test suite being executed

    Args:
        branch (str): The rpc-openstack branch to query for.

    Returns:
        tuple of (str, int): (code_name, major_version) OpenStack version. The
            tuple will be (None, None) if the branch doesn't match known values.
    """

    if branch in ['newton', 'newton-rc']:
        return 'Newton', 14
    elif branch in ['pike', 'pike-rc']:
        return 'Pike', 16
    elif branch in ['queens', 'queens-rc']:
        return 'Queens', 17
    elif branch in ['rocky', 'rocky-rc']:
        return 'Rocky', 18
    else:
        return 'master', 99


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('2c596d8f-7957-11e8-8017-6a00035510c0')
@pytest.mark.jira('ASC-234', 'ASC-1321', 'ASC-1601')
def test_openstack_release_version(host, openstack_properties):
    """Verify the swift endpoint status.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    r = next(gen_dict_extract('rpc_product_release',
                              host.ansible("setup")))
    expected_major = get_osa_version(r)[1]

    if expected_major == 99:
        pytest.skip('Test incompatible with RPC-O "master" branch.')

    assert openstack_properties['os_version_major'] == expected_major


@pytest.mark.test_id('0d8e4105-789e-11e8-8335-6a00035510c0')
@pytest.mark.jira('ASC-234', 'ASC-1321', 'ASC-1602')
def test_openstack_codename(host, openstack_properties):
    """Verify the swift endpoint status.

    Args:
        host (testinfra.host.Host): Testinfra host fixture.
        openstack_properties (dict): OpenStack facts and variables from Ansible
            which can be used to manipulate OpenStack objects.
    """

    r = next(gen_dict_extract('rpc_product_release',
                              host.ansible("setup")))
    expected_codename = get_osa_version(r)[0]

    if expected_codename == 'master':
        pytest.skip('Test incompatible with RPC-O "master" branch.')

    assert openstack_properties['os_version_codename'] == expected_codename
