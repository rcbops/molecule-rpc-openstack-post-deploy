import pytest_rpc.helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner
import json

"""ASC-157: Verify Cinder instance attachments
"""


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
          "-- bash -c '. /root/openrc ; ")
ssh_pre = ("ssh -o UserKnownHostsFile=/dev/null "
           "-o StrictHostKeyChecking=no -q ")


@pytest.mark.jira('asc-157')
@pytest.mark.test_id('01912ed1-547c-11e8-847a-6c96cfdb252f')
def test_cinder_verify_attach(host):
    # get list of volumes and server attatchments from utility container
    cmd = "{} cinder list --all-t '".format(os_pre)
    vol_table = host.run(cmd).stdout
    vol_list = helpers.parse_table(vol_table)[1]
    for vol in vol_list:
        vol_id = vol[0]
        attach_id = vol[7]
        if not attach_id:
            continue
        cmd1 = "{} openstack server show {} -f json '".format(os_pre, attach_id)
        res = host.run(cmd1)
        server = json.loads(res.stdout)
        hypervisor = server['OS-EXT-SRV-ATTR:hypervisor_hostname'].split('.')[0]
        instance_name = server['OS-EXT-SRV-ATTR:instance_name']
        # ATTATCHED test
        cmd2 = "{} {} virsh dumpxml {} | grep {}".format(ssh_pre, hypervisor,
                                                         instance_name, vol_id)
        host.run_expect([0], cmd2)
