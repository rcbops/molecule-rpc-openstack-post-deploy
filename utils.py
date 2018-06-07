import json

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


def get_image_id(image_name, run_on_host):
    """Get image id associated with image name"""
    cmd = "{} openstack image show {} -f json'".format(utility_container, image_name)
    output = run_on_host.run(cmd)
    try:
        result = json.loads(output.stdout)
    except ValueError:
        return

    if 'id' in result:
        return result['id']
    else:
        return


def create_bootable_volume(data, run_on_host):
    """Create a bootable volume using a json file"""

    volume_size = data['volume']['size']
    imageRef = data['volume']['imageRef']
    volume_name = data['volume']['name']

    cmd = "{} openstack volume create --size {} --image {} --availability-zone nova --bootable {}'".format(utility_container, volume_size, imageRef, volume_name)

    output = run_on_host.run(cmd)
    print ("\n----------- Create_bootable volume output: ----------\n")
    print output.stdout
    print("\n---- End of create bootable volume output -------\n")


def verify_volume(volume_name, run_on_host):
    """Verify if a volume is existing"""
    cmd = "{} openstack volume list'".format(utility_container)
    output = run_on_host.run(cmd)
    assert volume_name in output.stdout


def delete_volume(volume_name, run_on_host):
    """Delete volume"""
    volume_id = get_volume_id(volume_name, run_on_host)
    cmd = "{} openstack volume delete --purge {}'".format(utility_container, volume_id)
    output = run_on_host.run(cmd)
    assert volume_name not in output.stdout


def get_volume_id(volume_name, run_on_host):
    """Get volume id associated with volume name"""
    cmd = "{} openstack volume show {} -f json'".format(utility_container, volume_name)
    output = run_on_host.run(cmd)
    try:
        result = json.loads(output.stdout)
    except ValueError:
        return

    if 'id' in result:
        return result['id']
    else:
        return


def parse_table(ascii_table):
    header = []
    data = []
    for line in filter(None, ascii_table.split('\n')):
        if '-+-' in line:
            continue
        if not header:
            header = filter(lambda x: x != '|', line.split())
            continue
        data.append([''] * len(header))
        splitted_line = filter(lambda x: x != '|', line.split())
        for i in range(len(splitted_line)):
            data[-1][i] = splitted_line[i]
    return header, data
