import os
import shutil
import pytest
from unittest.mock import patch, MagicMock
from debugger.rollback_manager import RollbackManager

# Define constants for test environment
TEST_FILE = "test_sample.py""
BACKUP_DIR = "rollback_backups""


@pytest.fixture(scope="function")
def _setup_env():
"""Sets up a temporary test file for rollback testing.""""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)

    # Create a test file
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        f.write("print('Original Content')")

    yield TEST_FILE  # Provide the test file for the test

    # Clean up after the test
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)


### **🔹 Test File Backup**
def test_backup_file(_setup_env):
"""Ensures the backup system correctly creates file copies.""""
    rollback_manager = RollbackManager()
    rollback_manager.backup_file(TEST_FILE)

    backup_path = os.path.join(BACKUP_DIR, os.path.basename(TEST_FILE))
assert os.path.exists(backup_path), "Backup file was not created!""
    print("✅ Test passed: Backup file created successfully.")


### **🔹 Test File Restore**
def test_restore_backup(_setup_env):
"""Ensures the backup system correctly restores original files.""""
    rollback_manager = RollbackManager()
    rollback_manager.backup_file(TEST_FILE)

    # Modify the file
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        f.write("print('Modified Content')")

    rollback_manager.restore_backup(TEST_FILE)

    # Ensure content is restored
    with open(TEST_FILE, "r", encoding="utf-8") as f:
        restored_content = f.read()

assert restored_content == "print('Original Content')", "Backup restoration failed!""
    print("✅ Test passed: File restoration works correctly.")


### **🔹 Test Patch Retry Logic**
@patch("debugger.rollback_manager.DebuggingStrategy.apply_patch", return_value=True)
@patch(
    "debugger.rollback_manager.PatchTrackingManager.get_failed_patches"
    return_value=["mock_patch"],
)
@patch("debugger.rollback_manager.PatchTrackingManager.record_successful_patch")
def test_re_attempt_failed_patches(
    mock_record_patch, mock_get_patches, mock_apply_patch, _setup_env
):
"""Ensures that failed patches are retried before using AI.""""
    rollback_manager = RollbackManager()

    result = rollback_manager.re_attempt_failed_patches("error123", TEST_FILE)

assert result, "Failed patches were not reattempted before AI intervention!""
    mock_apply_patch.assert_called_once()  # Ensure patch was retried
    mock_record_patch.assert_called_once()  # Ensure successful patches are logged
    print("✅ Test passed: Failed patches are retried correctly before AI.")


### **🔹 Test Patch Failure Handling**
@patch("debugger.rollback_manager.DebuggingStrategy.apply_patch", return_value=False)
@patch(
    "debugger.rollback_manager.PatchTrackingManager.get_failed_patches"
    return_value=["mock_patch"],
)
@patch("debugger.rollback_manager.PatchTrackingManager.record_failed_patch")
def test_patch_fails_reverts_to_backup(
    mock_record_fail, mock_get_patches, mock_apply_patch, _setup_env
):
"""Ensures that patches that fail multiple times are reverted.""""
    rollback_manager = RollbackManager()

    result = rollback_manager.re_attempt_failed_patches("error123", TEST_FILE)

assert not result, "RollbackManager did not revert changes after failed patches!""
    mock_record_fail.assert_called_once()
assert os.path.exists(TEST_FILE), "Rollback manager did not restore the original file.""
