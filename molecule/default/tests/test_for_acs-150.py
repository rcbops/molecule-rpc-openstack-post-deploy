import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('non-existing-hosts')


class TestForRPC10PlusPostDeploymentQCProcess(object):
    """This class define all test cases that need implemented for ticket:
     https://rpc-openstack.atlassian.net/browse/ASC-150
     """

    @pytest.mark.test_id('d7fc308a-432a-11e8-9b02-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_reboot_physical_devices(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3197-432a-11e8-829b-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_galera_cluster(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3423-432a-11e8-aaa8-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_ceph_deploy(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3507-432a-11e8-8667-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_configed_quotas(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3621-432a-11e8-a95a-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_configed_networks(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc36f3-432a-11e8-87e9-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_updated_glance_image(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc380a-432a-11e8-9fc0-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_build_instances_on_compute_node(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc38fa-432a-11e8-ae81-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_floating_ip_nats(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc39f5-432a-11e8-99b4-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_correct_number_rabbitmq_per_connection(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3ab0-432a-11e8-ab7d-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_create_cinder_volume(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3bca-432a-11e8-8f27-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_write_to_attached_volume_partition(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3c87-432a-11e8-bfa2-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_create_volume_on_image_on_glance(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3d80-432a-11e8-a735-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_create_snapshot_of_an_instance(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3e85-432a-11e8-a9a2-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_mbu_installation(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc3f4c-432a-11e8-bf4f-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_ssl_config_f5(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc412e-432a-11e8-ae40-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_console_horizon(self, host):
        """See RPC 10+ Post-Deployment QC process document"""

    @pytest.mark.test_id('d7fc4407-432a-11e8-b65b-6a00035510c0')
    @pytest.mark.skip(reason='Need implementation')
    @pytest.mark.jira('ASC-150')
    def test_verify_kibana_horizon_access_with_no_ssh(self, host):
        """See RPC 10+ Post-Deployment QC process document"""
