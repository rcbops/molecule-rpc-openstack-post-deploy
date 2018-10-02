import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('non-existing-hosts')


class TestForRPC10PlusPostDeploymentQCProcess(object):
    """This class define all test cases that need implemented for ticket:
     https://rpc-openstack.atlassian.net/browse/ASC-150
     """

    @pytest.mark.test_id('d7fc3423-432a-11e8-aaa8-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150', 'ASC-235')
    def test_verify_ceph_deploy(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3f4c-432a-11e8-bf4f-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150', 'ASC-263')
    def test_verify_ssl_config_f5(self, host):
        """See RPC 10+ Post-Deployment QC process document"""
