import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('non-existing-hosts')


class TestForRPC10PlusPostDeploymentQCProcess(object):
    """This class define all test cases that need implemented for ticket:
     https://rpc-openstack.atlassian.net/browse/ASC-150
     """

    @pytest.mark.skip(reason='Need implementation')
    def test_reboot_physical_devices(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_galera_cluster(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_rpc_version(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_ceph_deploy(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_configed_quotas(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_configed_networks(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_updated_glance_image(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_build_instances_on_compute_node(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_floating_ip_nats(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_correct_number_rabbitmq_per_connection(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_create_cinder_volume(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_write_to_attached_volume_partition(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_create_volume_on_image_on_glance(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_create_snapshot_of_an_instance(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_mbu_installation(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_ssl_config_f5(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_ansible_playbook(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_console_horizon(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.skip(reason='Need implementation')
    def test_verify_kibana_horizon_access_with_no_ssh(self, host):
        """See RPC 10+ Post-Deployment QC process document"""
