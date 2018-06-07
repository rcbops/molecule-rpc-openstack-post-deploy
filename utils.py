import json
from time import sleep

utility_container = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
                     "-- bash -c '. /root/openrc ; ")


def get_id_by_name(service_type, service_name, run_on_host):
    """Get the id associated with name"""
    cmd = "{} openstack {} show \'{}\' -f json'".format(utility_container, service_type, service_name)
    output = run_on_host.run(cmd)
    try:
        result = json.loads(output.stdout)
    except ValueError:
        return

    if 'id' in result:
        return result['id']
    else:
        return


def create_instance(data, run_on_host):
    """Create an instance from source (a glance image or a snapshot)
    Args:
        data (dict): a dictionary of data. A sample of data as below:
                    data_image = {
                        "instance_name": instance_name,
                        "from_source": 'image',
                        "source_name": image_name,
                        "flavor": flavor,
                        "network_name": network,
                    }
        run_on_host (testinfra.host.Host): A hostname where the command is being executed.
    Example:
    `openstack server create --image <image_id> flavor <flavor> network <network_name> server/instance_name`
    `openstack server create --snapshot <snapshot_id> flavor <flavor> network <network_name> server/instance_name`
    """
    from_source = data['from_source']
    source_id = get_id_by_name(str(data['from_source']), str(data['source_name']), run_on_host)
    flavor = data['flavor']
    network_id = get_id_by_name('network', str(data['network_name']), run_on_host)
    instance_name = data['instance_name']

    cmd = "{} openstack server create --{} {} --flavor {} --nic net-id={} {} --wait'".format(utility_container, from_source, source_id, flavor, network_id, instance_name)

    run_on_host.run_expect([0], cmd)


def verify_asset_in_list(service_type, service_name, run_on_host):
    """Verify if a volume/server/image is existing"""
    cmd = "{} openstack {} list'".format(utility_container, service_type)
    output = run_on_host.run(cmd)
    assert service_name in output.stdout


def stop_server_instance(instance_name, run_on_host):
    instance_id = get_id_by_name('server', instance_name, run_on_host)

    cmd = "{} openstack server stop {}'".format(utility_container, instance_id)
    run_on_host.run_expect([0], cmd)


def get_status_by_name(service_type, service_name, run_on_host):
    """Getting status of a service"""
    service_id = get_id_by_name(service_type, service_name, run_on_host)
    cmd = "{} openstack {} show {} -f json'".format(utility_container, service_type, service_id)
    output = run_on_host.run(cmd)
    try:
        result = json.loads(output.stdout)
    except ValueError:
        return

    if 'status' in result:
        return result['status']
    else:
        return


def get_expected_status(service_type, service_name, expected_status, run_on_host, retries=10):
    for i in range(0, retries):
        while True:
            try:
                assert (expected_status == get_status_by_name(service_type, service_name, run_on_host))
            except Exception:
                print ("\n Trying again in 5 seconds.....\n")
                sleep(5)
                continue
            break


def create_snapshot_from_instance(snapshot_name, instance_name, run_on_host):
    """Create snapshot on an instance"""
    instance_id = get_id_by_name('server', instance_name, run_on_host)
    cmd = "{} openstack server image create --name {} --wait {}'".format(utility_container, snapshot_name, instance_id)

    run_on_host.run_expect([0], cmd)


def delete_it(service_type, service_name, run_on_host):
    id = get_id_by_name(service_type, service_name, run_on_host)
    cmd = "{} openstack {} delete {}'".format(utility_container, service_type, id)

    run_on_host.run_expect([0], cmd)
