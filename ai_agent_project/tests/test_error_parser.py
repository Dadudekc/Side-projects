"""

This module includes tests for the ErrorParser class. Specifically, it tests whether:

    - ErrorParser can correctly extract failures from valid pytest output (test_parse_test_failures_valid).
    - ErrorParser can handle an empty pytest output gracefully (test_parse_test_failures_empty).
    - ErrorParser can correctly identify output with no failures (test_parse_test_failures_no_failures).
    - ErrorParser can handle pytest output with unexpected formatting (test_parse_test_failures_malformed).

Fixtures
"""

import logging

import pytest
from ai_engine.models.debugger.error_parser import ErrorParser

logger = logging.getLogger("TestErrorParser")


@pytest.fixture
def parser():
    """Fixture to initialize ErrorParser."""
    return ErrorParser()


def test_parse_test_failures_valid(parser):
    """Tests if ErrorParser correctly extracts failures from valid pytest output."""
    pytest_output = """
    ==================== FAILURES ====================
    FAILED tests/test_example.py::test_addition - AssertionError: 1 + 1 != 3
    FAILED tests/test_math.py::test_divide_by_zero - ZeroDivisionError: division by zero
    ==================== SUMMARY ====================
    """

    failures = parser.parse_test_failures(pytest_output)

    assert len(failures) == 2
    assert failures[0]["file"] == "tests/test_example.py"
    assert failures[0]["test"] == "test_addition"
    assert failures[0]["error"] == "AssertionError: 1 + 1 != 3"
    assert failures[1]["file"] == "tests/test_math.py"
    assert failures[1]["test"] == "test_divide_by_zero"
    assert failures[1]["error"] == "ZeroDivisionError: division by zero"


def test_parse_test_failures_empty(parser):
    """Tests if ErrorParser handles empty pytest output gracefully."""
    pytest_output = ""

    failures = parser.parse_test_failures(pytest_output)

    assert failures == []  # Should return an empty list


def test_parse_test_failures_no_failures(parser):
    """Tests if ErrorParser correctly identifies output with no failures."""
    pytest_output = """
    ==================== TESTS PASSED ====================
    tests/test_example.py::test_addition PASSED
    tests/test_math.py::test_divide_by_zero PASSED
    ==================== SUMMARY ====================
    """

    failures = parser.parse_test_failures(pytest_output)

    assert failures == []  # Should return an empty list


def test_parse_test_failures_malformed(parser):
    """Tests if ErrorParser can handle pytest output with unexpected formatting."""
    pytest_output = """
    ==================== FAILURES ====================
    FAILED - tests/test_example.py::test_addition: AssertionError
    FAILED tests/test_math.py: test_divide_by_zero - ZeroDivisionError division by zero
    """

    failures = parser.parse_test_failures(pytest_output)

    # Expected to capture both correctly formatted failures
    assert len(failures) == 2

    assert failures[0]["file"] == "tests/test_example.py"
    assert failures[0]["test"] == "test_addition"
    assert failures[0]["error"] == "AssertionError"

    assert failures[1]["file"] == "tests/test_math.py"
    assert failures[1]["test"] == "test_divide_by_zero"
    assert failures[1]["error"] == "ZeroDivisionError division by zero"
