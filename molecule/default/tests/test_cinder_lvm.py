# -*- coding: utf-8 -*-
"""ASC-157: Verify Cinder volume as lvs on cinder node.
RPC 10+ manual test 14.
"""
# ==============================================================================
# Imports
# ==============================================================================
import os
import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('cinder_volume')


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.jira('asc-157')
@pytest.mark.test_id('b1e888fa-546a-11e8-9902-6c96cfdb252f')
def test_cinder_lvs_volume_on_node(os_api_conn, host):
    """Test to verify that a volume associated to a cinder host can be seen
        on that cinder host as a logical volume. If there is any snapshot
        created from the volume, then the snapshot is only seen on the cinder
        host that has that volume.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        host (testinfra.host.Host): Testinfra host fixture.
    """
    # get VolumeDetail
    vol_details = os_api_conn.block_storage.volumes()
    # get SnapshotDetails
    snapshot_details = os_api_conn.block_storage.snapshots()

    for vol in vol_details:
        chost = vol.to_dict()['host']
        chost = chost.split('@')[0].split('.')[0]
        vol_id = vol.to_dict()['id']

        # Ensure the host associated with the cinder volume is in cinder_volume
        # host group.
        assert chost in testinfra_hosts, \
            "The host '{}' associated with the cinder volume '{}' is not in " \
            "the cinder_hosts group.".format(chost, vol_id)

        # Get the hostname where the test is running (e.g 'cinder1', 'cinder2')
        current_host = host.run('hostname').stdout

        # Ensure the test only run on the cinder host associated with the
        # cinder volume
        if current_host == chost:
            cmd = "lvs |grep volume-{}".format(vol_id)
            assert host.run(cmd), "The command: '{}' failed to run on host " \
                                  "'{}'".format(cmd, current_host)

            for snapshot in snapshot_details:
                if snapshot.to_dict()['volume_id'] == vol_id:
                    snapshot_id = snapshot.to_dict()['id']
                    cmd = "lvs | grep _snapshot-{}".format(snapshot_id)
                    assert host.run(cmd), "The command: '{}' failed to run on" \
                                          "host '{}'.".format(cmd, current_host)
