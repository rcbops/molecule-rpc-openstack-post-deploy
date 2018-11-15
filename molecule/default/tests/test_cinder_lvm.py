import pytest_rpc_helpers as helpers
import os
import pytest
import testinfra.utils.ansible_runner

"""ASC-157: Verify Cinder volume as lvs on cinder node.

RPC 10+ manual test 14.
"""


# TODO: Put these values into ansible facts
cli_host = 'director'
cli_openrc_path = '/home/stack/overcloudrc'

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(cli_host)


os_pre = ". {} ; ".format(cli_openrc_path)
ssh_pre = ("ssh -o UserKnownHostsFile=/dev/null "
           "-o StrictHostKeyChecking=no -q ")


@pytest.mark.xfail(reason='ASC-1260 - The cinder host is not accessible in OSP')
@pytest.mark.jira('asc-157')
@pytest.mark.test_id('b1e888fa-546a-11e8-9902-6c96cfdb252f')
def test_cinder_lvs_volume_on_node(host):
    # get list of volumes and associated hosts from utility container
    cmd = "{} cinder list --all-t --fields os-vol-host-attr:host,status".format(os_pre)
    vol_table = host.run(cmd).stdout
    vol_hosts = helpers.parse_table(vol_table)[1]
    for vol, chost, status in vol_hosts:
        print vol, chost, status
        if status != 'available':
            continue
        chost = chost.split('@')[0].split('.')[0]
        # VOLEXISTS test
        cmd = "{} {} lvs | grep volume-{}".format(ssh_pre, chost, vol)
        host.run_expect([0], cmd)
        cmd = "{} cinder snapshot-list --all- --volume-id={}".format(os_pre, vol)
        snap_table = host.run(cmd).stdout
        snaps = helpers.parse_table(snap_table)[1]
        for snap in snaps:
            # SNAPEXISTS test
            snap_vol = snap[1]
            cmd = "{} {} lvs | grep _snapshot-{}".format(ssh_pre, chost, snap_vol)
            host.run_expect([0], cmd)
