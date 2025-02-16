import logging
from unittest.mock import MagicMock, patch

import pytest

from ai_engine.models.debugger.auto_fix_manager import AutoFixManager

logger = logging.getLogger("TestAutoFixManager")


@pytest.fixture
def retry_manager():
    """Fixture to initialize AutoFixManager."""
    return AutoFixManager()


# ** Test Running Tests Successfully**
@patch("ai_engine.models.debugger.test_retry_manager.subprocess.run")
def test_run_tests_success(mock_subprocess, retry_manager):
    """Tests if `run_tests` correctly detects no failures when all tests pass."""
    mock_subprocess.return_value.returncode = 0
    mock_subprocess.return_value.stdout = b"All tests passed!"

    failures = retry_manager.run_tests()

    assert failures == []  # No failures expected
    logger.info("✅ Test passed: No failures detected.")


# ** Test Running Tests With Failures**
@patch("ai_engine.models.debugger.test_retry_manager.subprocess.run")
def test_run_tests_with_failures(mock_subprocess, retry_manager):
    """Tests if `run_tests` correctly extracts failures from test output."""
    mock_subprocess.return_value.returncode = 1
    mock_subprocess.return_value.stdout = b"""
    FAILED tests/test_example.py - AssertionError: 1 + 1 != 3
    FAILED tests/test_math.py - ZeroDivisionError: division by zero
    """

    failures = retry_manager.run_tests()

    assert len(failures) == 2
    assert failures[0]["file"] == "tests/test_example.py"
    assert failures[0]["error"] == "AssertionError: 1 + 1 != 3"
    assert failures[1]["file"] == "tests/test_math.py"
    assert failures[1]["error"] == "ZeroDivisionError: division by zero"

    logger.info("✅ Test passed: Failures correctly extracted.")


# ** Test Patch Application Success**
@patch.object(
    AutoFixManager,
    "run_tests",
    return_value=[{"file": "tests/test_example.py", "error": "Mock Error"}],
)
@patch(
    "ai_engine.models.debugger.test_retry_manager.DebuggingStrategy.generate_patch",
    return_value="Mock Patch",
)
@patch(
    "ai_engine.models.debugger.test_retry_manager.DebuggingStrategy.apply_patch",
    return_value=True,
)
@patch(
    "ai_engine.models.debugger.test_retry_manager.PatchTrackingManager.record_successful_patch"
)
def test_patch_application_success(
    mock_record_patch,
    mock_apply_patch,
    mock_generate_patch,
    mock_run_tests,
    retry_manager,
):
    """Tests if a successful patch application prevents rollback."""
    result = retry_manager.retry_tests(max_retries=1)

    assert result["status"] == "success"
    mock_apply_patch.assert_called_once()  # ✅ Ensure apply_patch was called
    mock_generate_patch.assert_called_once()
    mock_record_patch.assert_called_once()
    logger.info("✅ Test passed: Patch applied successfully.")


# ** Test Rolling Back After Max Failures**
@patch(
    "ai_engine.models.debugger.test_retry_manager.PatchTrackingManager.record_failed_patch"
)
@patch(
    "ai_engine.models.debugger.test_retry_manager.DebuggingStrategy.apply_patch",
    return_value=False,
)
@patch(
    "ai_engine.models.debugger.test_retry_manager.DebuggingStrategy.generate_patch",
    return_value="Mock Patch",
)
@patch.object(
    AutoFixManager,
    "run_tests",
    return_value=[{"file": "tests/test_example.py", "error": "Mock Error"}],
)
@patch.object(AutoFixManager, "rollback_changes")
def test_patch_failure_rollback(
    mock_rollback,
    mock_run_tests,
    mock_generate_patch,
    mock_apply_patch,
    mock_record_fail,
    retry_manager,
):
    """Tests if rollback is triggered after max failed patch attempts."""
    result = retry_manager.retry_tests(max_retries=1)

    assert result["status"] == "error"
    mock_apply_patch.assert_called()  # ✅ Ensure apply_patch was actually called
    mock_record_fail.assert_called()
    mock_rollback.assert_called_once()
    logger.info("✅ Test passed: Rollback triggered after failed patch attempts.")
