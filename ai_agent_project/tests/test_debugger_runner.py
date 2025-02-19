"""
test_debugger_runner.py

Unit tests for the DebuggerRunner class.

Tests:
- test_run_tests_success: Ensures run_tests returns successful output.
- test_run_tests_failure: Checks that exceptions in run_tests are handled.
- test_retry_tests_success: Verifies that when fixes are applied successfully, retry_tests returns True.
- test_retry_tests_fail: Verifies that when fixes are ineffective, retry_tests returns False.
- test_retry_tests_no_failures: Verifies that if no failures are detected initially, retry_tests returns True.
"""

import pytest
from unittest.mock import MagicMock, patch
from ai_engine.models.debugger.debugger_runner import DebuggerRunner

@pytest.fixture
def debugger():
    """Fixture to initialize DebuggerRunner with mocks."""
    runner = DebuggerRunner()
    # Assign mocks directly to instance attributes
    runner.run_tests = MagicMock()
    runner.parser = MagicMock()
    runner.fixer = MagicMock()
    return runner

def test_run_tests_success(debugger):
    """Test successful test run with no failures."""
    debugger.run_tests.return_value = "3 passed"
    debugger.parser.parse_test_failures.return_value = []

    result = debugger.retry_tests(max_retries=3)

    assert result is True
    debugger.run_tests.assert_called_once()
    debugger.parser.parse_test_failures.assert_called_once()

def test_run_tests_failure(debugger):
    """Test a failed test run with no fixes applied."""
    debugger.run_tests.return_value = "2 failed, 1 passed"
    debugger.parser.parse_test_failures.return_value = [
        {"file": "test_a.py", "error": "AssertionError"},
        {"file": "test_b.py", "error": "TypeError"},
    ]
    # In this scenario, no fix is applied, so we expect the retry process to abort after the first attempt.
    debugger.fixer.apply_fix.return_value = False

    result = debugger.retry_tests(max_retries=3)

    assert result is False
    # Since there are 2 failures in the first attempt, apply_fix should be called 2 times.
    assert debugger.fixer.apply_fix.call_count == 2
    debugger.parser.parse_test_failures.assert_called_once_with("2 failed, 1 passed")

def test_retry_tests_success(debugger):
    """Test retry mechanism when fixes are applied successfully."""
    debugger.run_tests.side_effect = [
        "2 failed, 1 passed",  # First attempt: 2 failures
        "1 failed, 2 passed",  # Second attempt: 1 failure
        "3 passed",            # Final attempt: All tests pass
    ]
    debugger.parser.parse_test_failures.side_effect = [
        [
            {"file": "test_a.py", "error": "AssertionError"},
            {"file": "test_b.py", "error": "TypeError"},
        ],
        [{"file": "test_a.py", "error": "AssertionError"}],
        [],
    ]
    # Update side_effect to have three values in total (2 failures in attempt 1 + 1 failure in attempt 2 = 3 calls)
    debugger.fixer.apply_fix.side_effect = [True, True, True]

    result = debugger.retry_tests(max_retries=3)

    assert result is True
    # Now we expect 3 calls (total failures: 2 + 1 = 3)
    assert debugger.fixer.apply_fix.call_count == 3

def test_retry_tests_fail(debugger):
    """Test retry mechanism when fixes are ineffective."""
    debugger.run_tests.return_value = "2 failed, 1 passed"
    debugger.parser.parse_test_failures.return_value = [
        {"file": "test_a.py", "error": "AssertionError"},
        {"file": "test_b.py", "error": "TypeError"},
    ]
    debugger.fixer.apply_fix.side_effect = [False, False]  # Fix attempts fail

    result = debugger.retry_tests(max_retries=3)

    assert result is False
    assert debugger.fixer.apply_fix.call_count == 2  # Fixes attempted twice
    debugger.parser.parse_test_failures.assert_called_with("2 failed, 1 passed")

def test_retry_tests_no_failures(debugger):
    """Test when there are no test failures on the first run."""
    debugger.run_tests.return_value = "3 passed"
    debugger.parser.parse_test_failures.return_value = []  # No failures detected

    result = debugger.retry_tests(max_retries=3)

    assert result is True
    debugger.parser.parse_test_failures.assert_called_once()

# To run all tests, execute: pytest tests/test_debugger_runner.py -v
