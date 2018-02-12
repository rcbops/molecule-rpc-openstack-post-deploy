import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_ntp_package(host):
    assert host.package("ntp").is_installed


def test_ntp_file(host):
    f = host.file("/etc/ntp.conf")
    assert f.exists
    assert f.is_file


def test_ntp_file_content(host):
    f = host.file("/etc/ntp.conf")
    assert f.contains("0.us.pool.ntp.org")


def test_ntp_service(host):
    if host.system_info.distribution in ["debian", "ubuntu"]:
        ntp_daemon = "ntp"
    elif host.system_info.distribution == "centos":
        ntp_daemon = "ntpd"

    s = host.service(ntp_daemon)
    assert s.is_running
    assert s.is_enabled
