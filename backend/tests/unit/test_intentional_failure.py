"""Intentional test failure to verify PR health checks detect failures.

This file exists solely to test CI health check monitoring.
It should be removed after confirming health checks work correctly.
"""


def test_intentional_failure_for_ci_verification() -> None:
    """This test deliberately fails to trigger a CI health check failure."""
    expected = "health checks are working"
    actual = "this will not match"
    assert actual == expected, "INTENTIONAL FAILURE: Verifying CI health checks detect test failures"
