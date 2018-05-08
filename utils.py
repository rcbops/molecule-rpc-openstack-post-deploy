import re


def get_image_id(image_name, run_on_host):
    """Get image id associated with image name"""
    cmd = ". /root/openrc ; openstack image list | grep " + image_name
    output = run_on_host.run(cmd)
    result = re.search(r'(?<=\s)[a-zA-Z0-9\_\-]+(?=\s)', output.stdout)
    return result.group(0)


def create_bootable_volume(data, run_on_host):
    """Create a bootable volume using a json file"""

    cmd = ". /root/openrc ; openstack volume create " \
          "--size " + str(data['volume']['size']) \
          + " --image " + str(data['volume']['imageRef']) \
          + " --multi-attach --bootable " \
          + str(data['volume']['name'])

    output = run_on_host.run(cmd)
    print ("\ncreate_bootable volume output:\n")
    print output.stdout
    print("\nend\n")


def verify_volume(volume_name, run_on_host):
    """Verify if a volume is existing"""
    cmd = ". /root/openrc ; openstack volume list"
    output = run_on_host.run(cmd)
    assert volume_name in output.stdout


def delete_volume(volume_name, run_on_host):
    """Delete volume"""
    cmd = ". /root/openrc ; openstack volume delete --purge " + volume_name
    output = run_on_host.run(cmd)
    assert volume_name not in output.stdout
