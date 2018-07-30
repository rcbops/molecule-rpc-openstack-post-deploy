import os
import testinfra.utils.ansible_runner
import pytest
import pytest_rpc.helpers as helpers

"""ASC-298: Verify md5 sums of ring files using swift-recon tool

See RPC 10+ Post-Deployment QC process document
"""

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('os-infra_hosts')[:1]


@pytest.mark.test_id('d7fc49a8-432a-11e8-a2ea-6a00035510c0')
@pytest.mark.jira('ASC-298')
def test_verify_swift_ring_md5sums(host):
    """Verify the swift ring md5sums with local copy using swift-recon.

    """

    result = helpers.run_on_swift('swift-recon --md5', host)
    swift_data = helpers.parse_swift_recon(result.stdout)

    assert len(swift_data) > 2, "swift-recon did not return expected data"

    starting_line = swift_data[0][0]
    swift_count = next(iter([int(s) for s in starting_line.split() if
                             s.isdigit()]), None)

    # assert no errors found and that all hosts were matched
    for element in swift_data[1:]:
        assert '0 error' in element[-1], ('Errors found in {}'
                                          .format(element[0]))
        assert "{}/{} hosts matched".format(swift_count,
                                            swift_count) in element[-1], \
               "Not all hosts matched in {}" .format(element[0])
