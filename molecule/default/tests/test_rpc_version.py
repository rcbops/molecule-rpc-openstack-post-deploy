import os
import testinfra.utils.ansible_runner
import pytest
import re
import pytest_rpc.helpers as helpers

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

expected_codename, expected_major = helpers.get_osa_version_tuple()


@pytest.mark.test_id('2c596d8f-7957-11e8-8017-6a00035510c0')
@pytest.mark.jira('ASC-234')
def test_openstack_release_version(host):
    """Test to verify expected version of installed OpenStack

    Args:
        host(testinfra.host.Host): host fixture that will iterate over
        testinfra_hosts
    """

    # Expected example:
    # DISTRIB_RELEASE="r16.2.0"
    if expected_major.isdigit():
        pat = expected_major + r'.\d+.\d+'
    else:
        pat = r'\w+'
    expected_regex = re.compile('DISTRIB_RELEASE="r?{}"'.format(pat))
    release = host.file('/etc/openstack-release').content
    assert re.search(expected_regex, release)


@pytest.mark.test_id('0d8e4105-789e-11e8-8335-6a00035510c0')
@pytest.mark.jira('ASC-234')
def test_openstack_codename(host):
    """Test to verify expected codename of installed OpenStack

    Args:
        host(testinfra.host.Host): host fixture that will iterate over
        testinfra_hosts
    """

    # Expected example:
    # DISTRIB_CODENAME="Pike"
    expected_regex = r'DISTRIB_CODENAME="' + expected_codename + r'"'
    release = host.file('/etc/openstack-release').content
    assert re.search(expected_regex, release)


@pytest.mark.test_id('d7fc32ba-432a-11e8-81d4-6a00035510c0')
@pytest.mark.jira('ASC-234')
def test_rpc_version(host):
    """Test to verify expected version of installed RPC-OpenStack

    Args:
        host(testinfra.host.Host): host fixture that will iterate over
        testinfra_hosts
    """

    # Expected example:
    # r13.1.0rc1-987-gbb6b806
    expected_regex = r'[r]' + expected_major + r'.\d+.\d+'
    res = host.run("cd /opt/rpc-openstack ; git describe --tags")
    assert re.search(expected_regex, res.stdout)
