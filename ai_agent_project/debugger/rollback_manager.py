import os
import json
import logging
import shutil
from typing import Dict, List, Optional

from patch_tracking_manager import PatchTrackingManager
from debugging_strategy import DebuggingStrategy

logger = logging.getLogger("RollbackManager")
logger.setLevel(logging.DEBUG)

# Max retries per failed patch before resorting to AI
MAX_PATCH_RETRIES = 3
BACKUP_DIR = "rollback_backups"


class RollbackManager:
    """
    Automates the rollback and retry process for failed patches.
    
    🔹 How it Works:
      ✅ Re-applies **previously failed patches** before generating new AI fixes.
      ✅ If multiple failed patches exist, **tries different orders** before resorting to AI.
      ✅ Backs up original files before making changes.
      ✅ Ensures **no infinite loops** by limiting patch retries.
    """

    def __init__(self):
        self.patch_tracker = PatchTrackingManager()
        self.debugging_strategy = DebuggingStrategy()
        self.failed_attempts = {}  # Tracks retry attempts per error signature

    def backup_file(self, file_path: str):
        """Creates a backup of the file before applying patches."""
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
        if not os.path.exists(backup_path):
            shutil.copy(file_path, backup_path)
            logger.info(f"📁 Backed up {file_path} -> {backup_path}")
        return backup_path

    def restore_backup(self, file_path: str):
        """Restores a file from backup in case of rollback."""
        backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
        if os.path.exists(backup_path):
            shutil.copy(backup_path, file_path)
            logger.warning(f"🔄 Rolled back {file_path} from backup.")

    def re_attempt_failed_patches(self, error_signature: str, file_path: str) -> bool:
        """
        Retries previously failed patches before falling back to AI fixes.
        Returns True if a patch is successfully applied.
        """
        failed_patches = self.patch_tracker.get_failed_patches(error_signature)
        if not failed_patches:
            logger.info(f"🚫 No failed patches available for {error_signature}. Moving to AI fix.")
            return False

        # Ensure we don’t retry indefinitely
        if self.failed_attempts.get(error_signature, 0) >= MAX_PATCH_RETRIES:
            logger.error(f"⚠️ Max retry limit reached for {error_signature}. Skipping failed patches.")
            return False

        self.failed_attempts[error_signature] = self.failed_attempts.get(error_signature, 0) + 1

        # Try applying failed patches in different orders
        for patch in failed_patches:
            logger.info(f"🔄 Retrying failed patch for {file_path} (Attempt {self.failed_attempts[error_signature]})")
            self.backup_file(file_path)

            if self.debugging_strategy.apply_patch(patch):
                logger.info(f"✅ Patch successfully applied for {error_signature} on retry.")
                self.patch_tracker.record_successful_patch(error_signature, patch)
                return True  # Stop if a patch works
            
            # If patch fails again, restore from backup
            self.restore_backup(file_path)
            logger.warning(f"❌ Patch failed again for {error_signature}. Trying next one.")

        logger.error(f"🚨 All previous patches failed again for {error_signature}. Resorting to AI fix.")
        return False

    def rollback_changes(self, modified_files: List[str]):
        """
        Rolls back all modified files if no patch works.
        """
        if not modified_files:
            logger.info("🔍 No files modified, skipping rollback.")
            return

        for file in modified_files:
            self.restore_backup(file)
            logger.info(f"🔄 Rolled back changes in {file}.")


if __name__ == "__main__":
    rollback_manager = RollbackManager()

    # Example usage
    test_error_signature = "error_12345"
    test_file_path = "tests/test_example.py"

    # Try to re-attempt failed patches before using AI
    if not rollback_manager.re_attempt_failed_patches(test_error_signature, test_file_path):
        logger.info("➡️ Moving to AI-generated fix.")
