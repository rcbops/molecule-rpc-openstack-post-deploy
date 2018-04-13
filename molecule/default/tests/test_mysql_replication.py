import os
import testinfra.utils.ansible_runner
import pytest
import re

"""ASC-157: Perform Post Deploy System validations"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]

pre_cmd = ("lxc-attach -n $(lxc-ls -1 | grep galera | head -n 1) "
           "-- bash -c '")

@pytest.mark.jira('asc-157')
@pytest.mark.skip(reason='Need to confirm MNAIO expects this')
def test_mysql_replication(host):
    """Ensure that mysql replication has two slaves running"""

    cmd = '{} mysql -e "show slave status \G"\''.format(pre_cmd)
    res = host.run(cmd)
    assert len(re.findall(r'Slave_(IO|SQL)_Running', res.stdout)) == 2
