"""
This module provides unit tests for the RollbackManager in the 'ai_engine.models.debugger' package.

Tested behaviors:
- Rollback is triggered when a patch fails.
- Failed patches are retried before falling back to AI.
- Max retry attempts are properly enforced.

Uses pytest and unittest.mock for testing.
"""

import logging
from unittest.mock import MagicMock, patch
import pytest

from ai_engine.models.debugger.rollback_manager import RollbackManager

logger = logging.getLogger("TestRollbackManager")


@pytest.fixture
def rollback_manager():
    """Fixture to initialize RollbackManager."""
    return RollbackManager()


# ** Test Rollback is Triggered When a Patch Fails**
@patch.object(RollbackManager, "restore_backup")
def test_rollback_triggered_on_failure(mock_restore_backup, rollback_manager):
    """Rollback should be triggered after multiple failed patch attempts."""
    modified_files = ["tests/test_example.py"]
    rollback_manager.rollback_changes(modified_files)

    mock_restore_backup.assert_called_once_with("tests/test_example.py")
    logger.info("✅ Test passed: Rollback triggered when required.")


# ** Test Retrying Failed Patches Before AI Fallback**
@patch("ai_engine.models.debugger.rollback_manager.PatchTrackingManager.get_failed_patches", return_value=["Patch1", "Patch2"])
@patch("ai_engine.models.debugger.rollback_manager.DebuggingStrategy.apply_patch", side_effect=[False, True])  # First fails, second succeeds
@patch.object(RollbackManager, "backup_file")
@patch.object(RollbackManager, "restore_backup")
@patch("ai_engine.models.debugger.rollback_manager.PatchTrackingManager.record_successful_patch")
def test_re_attempt_failed_patches_success(
    mock_record_success,
    mock_restore,
    mock_backup,
    mock_apply_patch,
    mock_get_failed_patches,
    rollback_manager,
):
    """Failed patches should be retried, succeeding before falling back to AI."""
    error_signature = "error_12345"
    file_path = "tests/test_example.py"

    result = rollback_manager.re_attempt_failed_patches(error_signature, file_path)

    assert result is True  # ✅ The second patch should succeed
    mock_apply_patch.assert_called()  # ✅ Patches were attempted
    mock_record_success.assert_called_once()  # ✅ Successful patch recorded
    assert mock_backup.call_count == 2  # ✅ One backup per attempted patch
    mock_restore.assert_called_once()  # ✅ Restore should be called only after the first failure

    logger.info("✅ Test passed: Failed patches were retried and a successful one was found.")


# ** Test Max Retry Limit Enforcement**
@patch("ai_engine.models.debugger.rollback_manager.PatchTrackingManager.get_failed_patches", return_value=["Patch1", "Patch2"])
@patch("ai_engine.models.debugger.rollback_manager.DebuggingStrategy.apply_patch", return_value=False)  # All patches fail
@patch.object(RollbackManager, "backup_file")
@patch.object(RollbackManager, "restore_backup")
def test_max_retry_limit(
    mock_restore,
    mock_backup,
    mock_apply_patch,
    mock_get_failed_patches,
    rollback_manager,
):
    """Rollback should stop retrying after reaching max retry attempts."""
    error_signature = "error_12345"
    file_path = "tests/test_example.py"

    rollback_manager.failed_attempts[error_signature] = 3  # Simulate reaching max attempts

    result = rollback_manager.re_attempt_failed_patches(error_signature, file_path)

    assert result is False  # ✅ Should stop retrying
    mock_apply_patch.assert_not_called()  # ✅ No patches should be applied if max retries reached
    mock_restore.assert_not_called()  # ✅ No rollback since no new patch was applied

    logger.info("✅ Test passed: Max retry limit is properly enforced.")

