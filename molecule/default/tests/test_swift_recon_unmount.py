import os
import testinfra.utils.ansible_runner
import pytest
import pytest_rpc.helpers as helpers

"""ASC-298: Verify all swift rings are mounted using swift-recon tool

See RPC 10+ Post-Deployment QC process document
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('shared-infra_hosts')[:1]


@pytest.mark.test_id('4b0691b8-8b9e-11e8-8fb0-a860b622fd2c')
@pytest.mark.jira('ASC-298')
def test_verify_swift_ring_mounted(host):
    """Verify all swift rings are mounted using swift-recon.
    """

    result = helpers.run_on_swift('swift-recon --unmounted', host)
    swift_data = helpers.parse_swift_recon(result.stdout)

    assert len(swift_data) > 1, "swift-recon did not return expected data"

    # assert no output found for unmounted drives
    assert len(swift_data[1]) == 1, ('Unmounted swift drives found:\n{}'
                                     .format('\n'.join(swift_data[1])))
