import os
import re
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('non-existing-hosts')


class TestForRPC10PlusPostDeploymentQCProcessSwift(object):
    """This class define all test cases that need implemented for ticket:
     https://rpc-openstack.atlassian.net/browse/ASC-295
     """

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_swift_ring_has_data(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_object_ring_rebalanced(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_md5_and_mounted_drives(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_swift_stat(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_dispension_populate(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_dispension_report(self, host):
        """See RPC 10+ Post-Deployment QC process document"""
