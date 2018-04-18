import os
import testinfra.utils.ansible_runner
import pytest
import json

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

os_pre = ("lxc-attach -n $(lxc-ls -1 | grep utility | head -n 1) "
          "-- bash -c '. /root/openrc ; openstack ")


@pytest.mark.test_id('d7fc26a8-432a-11e8-8340-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_projects(host):
    """
    Ensure presence of basic projects
    """

    cmd = "{} project list -f json'".format(os_pre)
    res = host.run(cmd)
    projects = json.loads(res.stdout)
    project_names = [d['Name'] for d in projects]
    assert "admin" in project_names
    assert "service" in project_names


@pytest.mark.test_id('d7fc2770-432a-11e8-8af1-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_users(host):
    """
    Ensure presence of basic users
    """

    cmd = "{} user list --domain=default -f json'".format(os_pre)
    res = host.run(cmd)
    users = json.loads(res.stdout)
    user_names = [d['Name'] for d in users]
    assert "admin" in user_names
    assert "cinder" in user_names
    assert "dispersion" in user_names
    assert "glance" in user_names
    assert "heat" in user_names
    assert "keystone" in user_names
    assert "neutron" in user_names
    assert "nova" in user_names
    assert "placement" in user_names
    assert "swift" in user_names


@pytest.mark.test_id('d7fc2835-432a-11e8-a8a1-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_networks(host):
    """
    Ensure presence of basic networks
    """

    cmd = "{} network list -f json'".format(os_pre)
    res = host.run(cmd)
    networks = json.loads(res.stdout)
    network_names = [d['Name'] for d in networks]
    assert res.rc == 0
    assert len(network_names) > 0


@pytest.mark.test_id('d7fc28f5-432a-11e8-9af3-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_servers(host):
    """
    Ensure presence of basic nova servers
    """

    cmd = "{} server list -f json'".format(os_pre)
    res = host.run(cmd)
    assert res.rc == 0


@pytest.mark.test_id('d7fc2b45-432a-11e8-92c0-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_flavors(host):
    """
    Ensure presence of basic nova flavors
    """

    cmd = "{} flavor list -f json'".format(os_pre)
    res = host.run(cmd)
    flavors = json.loads(res.stdout)
    flavor_names = [d['Name'] for d in flavors]
    assert res.rc == 0
    assert len(flavor_names) > 0


@pytest.mark.test_id('d7fc2f02-432a-11e8-8e59-6a00035510c0')
@pytest.mark.jira('asc-157')
def test_image(host):
    """
    Ensure presence of basic glance images
    """

    cmd = "{} image list -f json'".format(os_pre)
    res = host.run(cmd)
    images = json.loads(res.stdout)
    image_names = [d['Name'] for d in images]
    res = host.run(cmd)
    assert res.rc == 0
    assert len(image_names) > 0
