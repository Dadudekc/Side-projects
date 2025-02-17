import logging
from unittest.mock import MagicMock, patch

import pytest

from ai_engine.models.debugger.debugger_runner import DebuggerRunner

logger = logging.getLogger("DebuggerRunner")


@pytest.fixture
def debugger():
    """Fixture to initialize DebuggerRunner."""
    return DebuggerRunner()


# ** Test Running Tests **
@patch("subprocess.run")
def test_run_tests_success(mock_subprocess, debugger):
    """Test successful pytest execution returning output."""
    mock_subprocess.return_value.stdout = "1 passed in 0.01s\n"
    mock_subprocess.return_value.stderr = ""

    output = debugger.run_tests()  # Fixed method call
    assert "1 passed" in output
    mock_subprocess.assert_called_once()


@patch("subprocess.run", side_effect=Exception("Pytest crashed"))
def test_run_tests_failure(mock_subprocess, debugger):
    """Test handling of a subprocess failure during test execution."""
    output = debugger.run_tests()  # Fixed method call
    assert "Error: Pytest crashed" in output


# ** Test Retrying Tests with Fixes **
@patch("ai_engine.models.debugger.debugger_runner.DebuggerRunner.run_tests")
@patch("ai_engine.models.debugger.debugger_runner.DebuggerRunner.parser")
@patch("ai_engine.models.debugger.debugger_runner.DebuggerRunner.fixer")
def test_retry_tests_success(mock_fixer, mock_parser, mock_run_tests, debugger):
    """Test retry mechanism when fixes are applied successfully."""
    mock_run_tests.side_effect = [
        "2 failed, 1 passed",  # First attempt: 2 failures
        "1 failed, 2 passed",  # Second attempt: 1 failure
        "3 passed",  # Final attempt: All tests pass
    ]

    mock_parser.parse_test_failures.side_effect = [
        [
            {"file": "test_a.py", "error": "AssertionError"},
            {"file": "test_b.py", "error": "TypeError"},
        ],
        [{"file": "test_a.py", "error": "AssertionError"}],
        [],
    ]

    mock_fixer.apply_fix.return_value = True

    result = debugger.retry_tests(max_retries=3)  # Fixed method call
    assert result is True
    assert mock_fixer.apply_fix.call_count == 2  # Fixes were attempted


@patch("ai_engine.models.debugger.debugger_runner.DebuggerRunner.run_tests", return_value="2 failed, 1 passed")
@patch("ai_engine.models.debugger.debugger_runner.DebuggerRunner.parser")
@patch("ai_engine.models.debugger.debugger_runner.DebuggerRunner.fixer")
def test_retry_tests_fail(mock_fixer, mock_parser, mock_run_tests, debugger):
    """Test retry mechanism when fixes are ineffective."""
    mock_parser.parse_test_failures.return_value = [
        {"file": "test_a.py", "error": "AssertionError"},
        {"file": "test_b.py", "error": "TypeError"},
    ]

    mock_fixer.apply_fix.return_value = False  # No fixes are applied

    result = debugger.retry_tests(max_retries=3)  # Fixed method call
    assert result is False
    assert mock_fixer.apply_fix.call_count == 2  # Fix attempts were made but failed


# ** Test No Failures Case **
@patch("ai_engine.models.debugger.debugger_runner.DebuggerRunner.run_tests", return_value="3 passed")
@patch("ai_engine.models.debugger.debugger_runner.DebuggerRunner.parser")
def test_retry_tests_no_failures(mock_parser, mock_run_tests, debugger):
    """Test when there are no test failures on the first run."""
    mock_parser.parse_test_failures.return_value = []  # No failures

    result = debugger.retry_tests(max_retries=3)  # Fixed method call
    assert result is True
    assert mock_parser.parse_test_failures.call_count == 1  # Only runs once


# ** Run All Tests with: **
# pytest test_debugger_runner.py -v