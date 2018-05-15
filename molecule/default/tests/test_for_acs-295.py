import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('non-existing-hosts')


class TestForRPC10PlusPostDeploymentQCProcessSwift(object):
    """This class define all test cases that need implemented for ticket:
     https://rpc-openstack.atlassian.net/browse/ASC-295
     """

    @pytest.mark.test_id('d7fc460f-432a-11e8-bd68-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-295')
    def test_verify_swift_ring_has_data(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc480f-432a-11e8-937e-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-295')
    def test_object_ring_rebalanced(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc49a8-432a-11e8-a2ea-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-295')
    def test_verify_md5_and_mounted_drives(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc4b42-432a-11e8-9ef9-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-295')
    def test_verify_swift_stat(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc4cdc-432a-11e8-a5dc-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-295')
    def test_verify_dispension_populate(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc4e61-432a-11e8-bcf5-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-295')
    def test_verify_dispension_report(self, host):
        """See RPC 10+ Post-Deployment QC process document"""
