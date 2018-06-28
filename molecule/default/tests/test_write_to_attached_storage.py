import os
import testinfra.utils.ansible_runner
import pytest
import json
import re
import pytest_rpc.helpers as helpers
from time import sleep

"""ASC-257: Attach a volume to an instance, create a partition and filesystem
on it, and verify you can write to it. """

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
          "-- bash -c '. /root/openrc ; openstack ")
os_post = "'"

ssh = "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
       -i ~/.ssh/rpc_support ubuntu@{}"

key_name = 'rpc_support'


@pytest.mark.test_id('3d77bc35-7a21-11e8-90d1-6a00035510c0')
@pytest.mark.jira('ASC-257')
def test_volume_attached(host):
    vars = host.ansible('include_vars',
                        'file=./vars/main.yml')['ansible_facts']

    server_name = vars['test_server']
    volume_name = vars['test_volume']

    floating_ip = create_floating_ip('GATEWAY_NET', host)
    attach_floating_ip(server_name, floating_ip, host)
    attach_volume_to_server(volume_name, server_name, host)

    # ensure attachment and retrieve associated device
    cmd = "{} volume show  \
           -f json \
           {} {}".format(os_pre, volume_name, os_post)
    res = host.run(cmd)
    volume = json.loads(res.stdout)
    assert len(volume['attachments']) == 1
    device = volume['attachments'][0]['device']

    # ensure we can SSH to server
    backoff = 1
    for i in range(10):
        try:
            cmd = "{} 'sudo ls'".format(ssh.format(floating_ip))
            ssh_attempt = host.run_expect([0], cmd)
        except AssertionError:
            sleep(backoff)
            backoff = backoff * 2
        else:
            break

    assert ssh_attempt.rc == 0

    # create partition
    cmd = "{} 'echo -e \"o\\nn\\np\\n1\\n\\n\\nw\" \
           | sudo fdisk {}'".format(ssh.format(floating_ip), device)
    res = host.run(cmd)
    assert "Created a new partition 1 of type 'Linux'" in res.stdout

    # create filesystem
    cmd = "{} 'sudo mkfs.ext4 {}1'".format(ssh.format(floating_ip), device)
    res = host.run(cmd)
    assert re.search(r'blocks and filesystem accounting information:.*done',
                     res.stdout)

    # mount partition
    cmd = "{} 'sudo mount {}1 /mnt'".format(ssh.format(floating_ip), device)
    host.run(cmd)

    # verify mounted partition
    cmd = "{} 'sudo df'".format(ssh.format(floating_ip))
    res = host.run(cmd)
    assert device in res.stdout

    # write data to partition
    cmd = "{} 'echo \"Call me Ishmael.\" > \
           moby-dick.txt'".format(ssh.format(floating_ip))
    host.run_expect([0], cmd)
    cmd = "{} 'sudo mv moby-dick.txt /mnt/'".format(ssh.format(floating_ip))
    host.run_expect([0], cmd)

    # verify data
    cmd = "{} 'sudo cat /mnt/moby-dick.txt'".format(ssh.format(floating_ip))
    res = host.run(cmd)
    assert 'Call me Ishmael' in res.stdout

    # unmount partition
    cmd = "{} 'sudo umount /mnt'".format(ssh.format(floating_ip))
    host.run_expect([0], cmd)

    # verify absence of data
    cmd = "{} 'sudo cat /mnt/moby-dick.txt'".format(ssh.format(floating_ip))
    res = host.run(cmd)
    assert 'No such file' in res.stderr

    # mount partition
    cmd = "{} 'sudo mount {}1 /mnt'".format(ssh.format(floating_ip), device)
    host.run_expect([0], cmd)

    # verify data
    cmd = "{} 'sudo cat /mnt/moby-dick.txt'".format(ssh.format(floating_ip))
    res = host.run(cmd)
    assert 'Call me Ishmael' in res.stdout
