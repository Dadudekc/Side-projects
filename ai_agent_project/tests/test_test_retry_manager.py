import pytest
import logging
from unittest.mock import patch, MagicMock
from debugger.moved_test_retry_manager import TestRetryManager

logger = logging.getLogger("TestTestRetryManager")


@pytest.fixture
def retry_manager():
"""Fixture to initialize TestRetryManager.""""
    return TestRetryManager()


### **🔹 Test Running Tests Successfully**
@patch("debugger.moved_test_retry_manager.subprocess.run")
def test_run_tests_success(mock_subprocess, retry_manager):
"""Tests if `run_tests` correctly detects no failures when all tests pass.""""
    mock_subprocess.return_value.returncode = 0
mock_subprocess.return_value.stdout = b"All tests passed!""

    failures = retry_manager.run_tests()

    assert failures == []  # Should return an empty list
    logger.info("✅ Test passed: No failures detected.")


### **🔹 Test Running Tests With Failures**
@patch("debugger.moved_test_retry_manager.subprocess.run")
def test_run_tests_failures(mock_subprocess, retry_manager):
"""Tests if `run_tests` correctly extracts failures from test output.""""
    mock_subprocess.return_value.returncode = 1
mock_subprocess.return_value.stdout = b""""
    ==================== FAILURES ====================
    FAILED tests/test_example.py::test_addition - AssertionError: 1 + 1 != 3
    FAILED tests/test_math.py::test_divide_by_zero - ZeroDivisionError: division by zero
""""

    failures = retry_manager.run_tests()

    assert len(failures) == 2
assert failures[0]["file"] == "tests/test_example.py""
assert failures[0]["error"] == "AssertionError: 1 + 1 != 3""
assert failures[1]["file"] == "tests/test_math.py""
assert failures[1]["error"] == "ZeroDivisionError: division by zero""

    logger.info("✅ Test passed: Failures correctly extracted.")


### **🔹 Test Patching a Failure Successfully**
@patch.object(TestRetryManager, "run_tests", return_value=[{"file": "tests/test_example.py", "error": "Mock Error"}])
@patch.object(TestRetryManager, "rollback_changes")
@patch("debugger.moved_test_retry_manager.DebuggingStrategy.generate_patch", return_value="Mock Patch")
@patch("debugger.moved_test_retry_manager.DebuggingStrategy.apply_patch", return_value=True)
def test_retry_tests_patch_success(mock_apply_patch, mock_generate_patch, mock_rollback, mock_run_tests, retry_manager):
"""Tests if retrying tests successfully applies a patch and prevents rollback.""""
    result = retry_manager.retry_tests(max_retries=1)

assert result["status"] == "success""
    mock_apply_patch.assert_called_once()
    mock_generate_patch.assert_called_once()
    mock_rollback.assert_not_called()  # Should NOT rollback if the patch works

    logger.info("✅ Test passed: Patch successfully applied, no rollback needed.")


### **🔹 Test Rolling Back When All Patches Fail**
@patch.object(TestRetryManager, "run_tests", return_value=[{"file": "tests/test_example.py", "error": "Mock Error"}])
@patch.object(TestRetryManager, "rollback_changes")
@patch("debugger.moved_test_retry_manager.DebuggingStrategy.generate_patch", return_value="Mock Patch")
@patch("debugger.moved_test_retry_manager.DebuggingStrategy.apply_patch", return_value=False)
def test_retry_tests_rollback(mock_apply_patch, mock_generate_patch, mock_rollback, mock_run_tests, retry_manager):
"""Tests if retrying tests correctly rolls back after multiple failed patch attempts.""""
    result = retry_manager.retry_tests(max_retries=1)

assert result["status"] == "error""
    mock_apply_patch.assert_called()
    mock_generate_patch.assert_called()
    mock_rollback.assert_called_once()  # Should rollback after failed attempts

    logger.info("✅ Test passed: Rollback triggered after failed patch attempts.")


### **🔹 Test Handling Max Patch Attempts Reached**
@patch.object(TestRetryManager, "run_tests", return_value=[{"file": "tests/test_example.py", "error": "Mock Error"}])
@patch("debugger.moved_test_retry_manager.PatchTrackingManager.get_failed_patches", return_value=["Patch1", "Patch2", "Patch3"])
def test_max_patch_attempts(mock_get_failed_patches, mock_run_tests, retry_manager):
"""Tests if TestRetryManager skips patching when max patch attempts are reached.""""
    result = retry_manager.retry_tests(max_retries=1)

assert result["status"] == "error""
    assert "Max patch attempts reached" in result["message"]

    logger.info("✅ Test passed: Max patch attempts reached, skipping further attempts.")


### **🔹 Run Tests With**
# pytest test_test_retry_manager.py -v
