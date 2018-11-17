# -*- coding: utf-8 -*-
# ==============================================================================
# Imports
# ==============================================================================
import os
# noinspection PyPackageRequirements
import yaml
import errno
import pytest
import shutil
import hashlib
# noinspection PyPackageRequirements
import paramiko
import subprocess
# noinspection PyPackageRequirements
import testinfra.utils.ansible_runner
from StringIO import StringIO

# ==============================================================================
# Globals
# ==============================================================================
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


# ==============================================================================
# Helpers
# ==============================================================================
def backup_remote_file(host, remote_path):
    """Create a backup of a remote file.

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json or
            molecule.yml
        remote_path (str): The absolute path to the file remote file.

    Returns:
        str: Contents of remote file.

    Raises:
        AssertionError: Failed to create a backup copy of remote file.
    """

    # Grab file contents
    contents = host.file(remote_path).content_string

    # Backup file
    cmd = "mv {} {}".format(remote_path, remote_path + '.bak')
    host.run_expect(expected=[0], command=cmd)

    return contents


def restore_remote_file(host, remote_path):
    """Restore a file that has a '.bak' copy. (

    WARNING! Do not append '.bak' to file path as it is already assumed!

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json or
            molecule.yml
        remote_path (str): The absolute path to the file remote file.

    Raises:
        AssertionError: Failed to restore backup copy of remote file.
    """

    # Restore file
    cmd = "mv {} {}".format(remote_path + '.bak', remote_path)
    host.run_expect(expected=[0], command=cmd)


def upload_file(host, remote_path, file_data):
    """Upload a file to a remote host.

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json or
            molecule.yml
        remote_path (str): The absolute path to the file remote file.
        file_data (str): The contents of the file to upload.

    Raises:
        OSError, IOError: Failure to upload file
    """

    # Init
    hostname = host.ansible.get_variables()['inventory_hostname']

    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username='root')

        with ssh.open_sftp() as sftp:
            sftp.putfo(StringIO(file_data), remote_path)


def download_glance_image(os_api_conn, image, download_path):
    """Download an image from Glance to the local machine.

    Args:
        os_api_conn (openstack.connection.Connection): Connection to the
            OpenStack Python API.
        image (openstack.image.v2.image.Image): The image to download from
            Glance.
        download_path (str): The path in which to download the image.

    Returns:
        dict: Information about the downloaded image.
            {'name',
             'disk_format',
             'container_format',
             'visibility',
             'local_path',
             'size'}

    Raises:
        AssertionError: Failed to backup the image.
    """

    try:
        os.makedirs(download_path)   # Ensure backup directory exists.
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(download_path):
            pass
        else:
            raise

    # Init
    md5 = hashlib.md5()  # MD5 hash for data integrity validation
    local_path = os.path.join(download_path, image.id)
    image_info = {'name': image.name,
                  'disk_format': image.disk_format,
                  'container_format': image.container_format,
                  'visibility': image.visibility,
                  'local_path': local_path,
                  'size': int(image.size)}

    with open(local_path, 'wb') as image_file:
        response = os_api_conn.image.download_image(image, stream=True)

        for chunk in response.iter_content(chunk_size=10485760):
            # With each chunk, add it to the hash to be computed.
            md5.update(chunk)

            image_file.write(chunk)

        assert response.headers["Content-MD5"] == md5.hexdigest()

    return image_info


def upload_glance_image(os_api_conn,
                        name,
                        local_path,
                        disk_format,
                        container_format,
                        visibility):
    """Upload an image from the local machine to Glance.

    Args:
        os_api_conn (openstack.connection.Connection): Connection to the
            OpenStack Python API.
        name (str): The human readable name for the image as it will appear in
            Glance.
        local_path (str): The path to the image file to upload to Glance.
        disk_format (str): The disk format for the Glance image.
        container_format (str): The container format for the Glance image.
        visibility (str): The visibility (e.g. public, private) for the Glance
            image.

    Raises:
        AssertionError: Failed to backup the image.
    """

    # Load image data into memory. YEAH, ALL OF IT!
    with open(local_path, 'rb') as image_file:
        data = image_file.read()

    os_api_conn.image.upload_image(name=name,
                                   data=data,
                                   disk_format=disk_format,
                                   container_format=container_format,
                                   visibility=visibility)


def delete_all_glance_images(os_api_conn):
    """Delete all Glance images.

    WARNING! I hope you backed everything up before doing this as it can't be
    reversed!

    Args:
        os_api_conn (openstack.connection.Connection): Connection to the
            OpenStack Python API.

    Raises:
        AssertionError: Failed to backup the image.
    """

    for image in os_api_conn.image.images():
        os_api_conn.image.delete_image(image, ignore_missing=False)


def run_openstack_ansible(host, playbook_path):
    """Execute a run of 'openstack-ansible' on target host.

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json or
            molecule.yml
        playbook_path (str): The absolute path to the playbook YAML file.

    Raises:
        AssertionError: The 'openstack-ansible' run failed.
    """

    # Execute 'openstack-ansible' on target host
    cmd = "openstack-ansible {}".format(playbook_path)
    host.run_expect(expected=[0], command=cmd)


# ==============================================================================
# Fixtures
# ==============================================================================
@pytest.fixture(scope='module')
def glance_vars(openstack_properties):
    """A dictionary of variables pertinent to Glance testing.

    Returns:
        dict: {deployment_host_ip: str
               os_image_backup_path: str
               os_glance_install_playbook_path: str
               openstack_user_config_path: str
               user_variables_path: str
               glance_nfs_mount_path: str
               glance_nfs_share_path: str}

    Raises:
        subprocess.CalledProcessError: Failed to collect IP of deployment host.
    """

    # Get deployment host IP
    cmd = r"ip addr show bond0 | grep -Po 'inet \K[\d.]+'"
    deployment_host_ip = subprocess.check_output(cmd, shell=True).rstrip()

    glance_var_dict = {
        'deployment_host_ip': deployment_host_ip,
        'os_image_backup_path': '/tmp/glance_image_backup',
        'os_glance_install_playbook_path':
            '/opt/openstack-ansible/playbooks/os-glance-install.yml',
        'openstack_user_config_path':
            '/etc/openstack_deploy/openstack_user_config.yml',
        'user_variables_path': '/etc/openstack_deploy/user_variables.yml',
        'glance_nfs_mount_path':
            str(openstack_properties['glance_nfs_mount_path']),
        'glance_nfs_share_path':
            str(openstack_properties['glance_nfs_share_path'])
    }

    return glance_var_dict


@pytest.fixture(scope='module')
def backup_glance_images(os_api_conn, glance_vars):
    """Backup all existing Glance images to the deployment host.

    WARNING! This fixture removes all images after they are successfully
    backed up locally! Image restoration *must* be handled independently.

    Args:
        os_api_conn (openstack.connection.Connection): Connection to the
            OpenStack Python API.
        glance_vars (dict): A dictionary of variables pertinent to Glance
            testing.

    Returns:
        list: A list of dictionaries with information about the image backups.
            {'name',
             'disk_format',
             'container_format',
             'visibility',
             'local_path',
             'size'}

    Raises:
        AssertionError: Failed to backup the image.
    """

    # Init
    backup_image_info = []

    # Backup
    for image in os_api_conn.image.images():
        # Download image locally
        backup_image_info.append(
            download_glance_image(
                os_api_conn,
                image,
                glance_vars['os_image_backup_path']
            )
        )

    yield backup_image_info

    # Teardown
    # Remove backup image files.
    shutil.rmtree(glance_vars['os_image_backup_path'])


@pytest.fixture(scope='module')
def enable_nfs_glance_client(host,
                             os_api_conn,
                             glance_vars,
                             backup_glance_images):
    """Update the OpenStack configuration files to enable NFS backed Glance and
    execute execute 'openstack-ansible' to enforce the changes.

    Args:
        host(testinfra.host.Host): A hostname in dynamic_inventory.json or
            molecule.yml
        os_api_conn (openstack.connection.Connection): Connection to the
            OpenStack Python API.
        glance_vars (dict): A dictionary of variables pertinent to Glance
            testing.
        backup_glance_images (list): A list of dictionaries with information
            about the image backups.

    Returns:
        list: A list of dictionaries with information about the image backups.
            {'name',
             'disk_format',
             'container_format',
             'visibility',
             'local_path',
             'size'}
    """

    # Init
    conf_files = {glance_vars['openstack_user_config_path']: {},
                  glance_vars['user_variables_path']: {}}
    nfs_client_info = [
        {
            'local_path': glance_vars['glance_nfs_mount_path'],
            'options': '_netdev,auto',
            'remote_path': glance_vars['glance_nfs_share_path'],
            'server': glance_vars['deployment_host_ip'],
            'type': 'nfs4'
        }
    ]

    # Backup files
    for conf_file in conf_files:
        conf_files[conf_file] = yaml.safe_load(
            backup_remote_file(host, conf_file)
        )

    # Update 'openstack_user_config'
    for i in range(1, 4):
        file_name = glance_vars['openstack_user_config_path']
        infra_host = "infra{}".format(i)
        infra_block = \
            conf_files[file_name]['infra_block'][infra_host]['container_vars']

        infra_block['glance_nfs_client'] = nfs_client_info

    # Update 'user_variables.yml'
    conf_files[glance_vars['user_variables_path']]['glance_default_store'] = \
        'file'

    # Upload updated OpenStack config files
    for conf_file in conf_files:
        upload_file(host,
                    conf_file,
                    yaml.safe_dump(conf_files[conf_file]))

    # Delete Glance images to set the Glance registry to a known good state
    delete_all_glance_images(os_api_conn)

    # Update the configuration of OpenStack infrastructure
    run_openstack_ansible(host, glance_vars['os_glance_install_playbook_path'])

    # Re-upload images back to Glance
    for image_info in backup_glance_images:
        upload_glance_image(os_api_conn,
                            name=image_info['name'],
                            local_path=image_info['local_path'],
                            disk_format=image_info['disk_format'],
                            container_format=image_info['container_format'],
                            visibility=image_info['visibility'])

    return backup_glance_images

    # Teardown
    # TODO: The bug 'RI-572' prevents switching Glance backend back to Swift
    # # Restore original Glance configuration
    # for conf_file in conf_files:
    #     restore_remote_file(host, os.path.join(conf_dir, conf_file))
    #
    # # Delete Glance images to set the Glance registry to a known good state
    # delete_all_glance_images(os_api_conn)
    #
    # # Update the configuration of OpenStack infrastructure
    # run_openstack_ansible(host, OS_GLANCE_INSTALL_PLAYBOOK_PATH)
    #
    # # Re-upload images back to Glance
    # for image_info in backup_glance_images:
    #     upload_glance_image(os_api_conn,
    #                         name=image_info['name'],
    #                         local_path=image_info['local_path'],
    #                         disk_format=image_info['disk_format'],
    #                         container_format=image_info['container_format'],
    #                         visibility=image_info['visibility'])


# ==============================================================================
# Tests
# ==============================================================================
@pytest.mark.test_id('3f62aa22-e7a1-11e8-9f0f-0025227c8120')
@pytest.mark.jira('ASC-1082')
def test_verify_images_stored_on_nfs(os_api_conn,
                                     glance_vars,
                                     enable_nfs_glance_client):
    """Verify that the images have been successfully saved onto the NFS share
    located on the deployment host. (localhost)

    Args:
        os_api_conn (openstack.connection.Connection): Connection to the
            OpenStack Python API.
        glance_vars (dict): A dictionary of variables pertinent to Glance
            testing.
        enable_nfs_glance_client (list): A list of dictionaries with information
            about the image backups.
    """

    for image_info in enable_nfs_glance_client:
        # Verify that a backed-up image name also exists in Glance
        glance_image_obj = os_api_conn.image.find_image(image_info['name'])
        assert glance_image_obj

        # Verify image exists on deployment host NFS share
        nfs_image_path = os.path.join(
            glance_vars['glance_nfs_share_path'],
            glance_image_obj.id
        )

        assert os.path.isfile(nfs_image_path)
        assert os.path.getsize(nfs_image_path) == image_info['size']
