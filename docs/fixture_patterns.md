# Fixture/Helper Locations

This Molecule test suite utilizes [pytest fixtures] extensively which are 
sourced from several different locations:

- [pytest-rpc] plug-in
- Local repository's '[conftest.py]'
- Contained within a pytest module ([Example])

The following sub-sections will cover the purpose for each location mentioned
above.

## The [pytest-rpc] Plug-in

The [pytest-rpc] plug-in contains fixtures and helpers that can generally be 
used when testing RPC-O or its constituent components. The vast majority of
fixtures used by this Molecule test suite are probably contained in [pytest-rpc] 
plug-in, so check that repo first when you have questions about a given fixture.

The main benefit of storing fixtures and helpers in the [pytest-rpc] plug-in 
is that common test code can be shared easily among many different [pytest] 
based test suites. However, storing common test code [pytest-rpc] plug-in does 
have several drawbacks:

1. Requires automation engineers to look in a separate location when using or
reading tests that utilize fixtures or helpers from the [pytest-rpc] plug-in.
2. Increases the difficultly of validating new or updated common test code
found in [pytest-rpc] plug-in. (See [Development Build Release Process])
3. Increases the development time for tests that require new release of 
the [pytest-rpc] plug-in.

Even with the aforementioned drawbacks the return on investment is still very
lucrative as long as automation engineers use due diligence when creating new
fixtures. Given the potentially high negative impact of development velocity,
the automation engineers should only place common test code in the[pytest-rpc]
plug-in when there is **high confidence** that said code will be used by other
[pytest] based RPC-O test suites.

## Local Repository's '[conftest.py]'

The benefits of using the local repository's '[conftest.py]' is that fixtures
and helpers placed in the '[conftest.py]' are accessible by all [pytest] test
modules automatically.

Common test code should be placed in the '[conftest.py]' when the following
criteria is satisfied:

1. The prospective fixture or helper **can only be used** by test cases found in
the current repository.
2. The prospective fixture or helper **will be used** by multiple [pytest] test
modules.

## Test Module

In the situation where a set of test cases in a module benefit from fixtures or
helpers, but no other test cases outside of the module would benefit then the
best strategy is to place the fixture or helper in the [pytest] test module.
(See this [Example])

[pytest fixtures]: https://docs.pytest.org/en/latest/fixture.html
[conftest.py]: ../molecule/default/tests/conftest.py
[pytest-rpc]: https://github.com/rcbops/pytest-rpc
[Example]: ../molecule/default/tests/test_instance_per_network_per_hypervisor.py
[pytest]: https://docs.pytest.org/en/latest/
[Development Build Release Process]: https://github.com/rcbops/pytest-rpc/blob/master/docs/release_process.rst#development-build-release-process
