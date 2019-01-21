# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import pytest


# ==============================================================================
# Test Cases
# ==============================================================================
@pytest.mark.test_id('3d77bc35-7a21-11e8-90d1-6a00035510c0')
@pytest.mark.jira('ASC-257', 'ASC-883', 'RI-417', 'ASC-1335')
def test_volume_attached(os_api_conn,
                         create_volume,
                         small_ubuntu_server,
                         ssh_connect):
    """Verify that an attached volume can be written to via the operating
    system.

    Args:
        os_api_conn (openstack.connection.Connection): An authorized API
            connection to the 'default' cloud on the OpenStack infrastructure.
        create_volume (def): A factory function for generating volumes.
        small_ubuntu_server (openstack.compute.v2.server.Server): Create a
            'm1.small' server instance with an Ubuntu image.
        ssh_connect (def): Create a connection to a server via SSH.
    """

    # Create blank volume.
    test_volume = create_volume(size=1)

    # Attach volume to server.
    attach_info = os_api_conn.attach_volume(wait=True,
                                            volume=test_volume,
                                            server=small_ubuntu_server,
                                            timeout=90)

    # Setup
    mount_point = '/mnt/test'
    mount_cmd = ("sudo mount {0}1 {1} &&"
                 "sudo chmod 777 {1}".format(attach_info.device, mount_point))
    umount_cmd = "sudo umount {}".format(mount_point)
    mkfs_cmd = "sudo mkfs.ext4 {}1".format(attach_info.device)
    test_data = 'Call me Ishmael.'
    test_file_path = '{}/test_file.txt'.format(mount_point)
    test_file_exists_cmd = "test -f {}".format(test_file_path)
    parted_mkpart_cmd = ("sudo parted -a opt {} "
                         "mkpart primary 0% 100%".format(attach_info.device))
    parted_mklabel_cmd = ("sudo parted {} "
                          "mklabel msdos".format(attach_info.device))
    create_mount_point_cmd = ("sudo mkdir -p {}".format(mount_point))

    # Connect to server through SSH
    ssh = ssh_connect(hostname=small_ubuntu_server.accessIPv4,
                      username='ubuntu',
                      retries=15)

    # Partition, format and mount drive
    assert ssh.exec_command(
        timeout=60,
        get_pty=True,
        command=parted_mklabel_cmd
    )[1].channel.recv_exit_status() == 0

    assert ssh.exec_command(
        timeout=60,
        get_pty=True,
        command=parted_mkpart_cmd
    )[1].channel.recv_exit_status() == 0

    assert ssh.exec_command(
        timeout=60,
        get_pty=True,
        command=mkfs_cmd
    )[1].channel.recv_exit_status() == 0

    assert ssh.exec_command(
        timeout=60,
        get_pty=True,
        command=create_mount_point_cmd
    )[1].channel.recv_exit_status() == 0

    assert ssh.exec_command(
        timeout=60,
        get_pty=True,
        command=mount_cmd
    )[1].channel.recv_exit_status() == 0

    # Write test data to mounted drive
    with ssh.open_sftp().open(test_file_path, 'w') as f:
        f.write(test_data)

    # Unmount
    assert ssh.exec_command(
        timeout=60,
        get_pty=True,
        command=umount_cmd
    )[1].channel.recv_exit_status() == 0

    # Verify that file does not exist
    assert ssh.exec_command(
        timeout=60,
        get_pty=True,
        command=test_file_exists_cmd
    )[1].channel.recv_exit_status() == 1

    # Remount
    assert ssh.exec_command(
        timeout=60,
        get_pty=True,
        command=mount_cmd
    )[1].channel.recv_exit_status() == 0

    # Verify test file data
    with ssh.open_sftp().open(test_file_path, 'r') as f:
        assert f.read() == test_data
