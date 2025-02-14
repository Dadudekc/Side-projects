import os
import shutil
import subprocess
import logging
from typing import Dict, Any, List
from debugging_strategy import DebuggingStrategy
from debugger_logger import DebuggerLogger
from patch_tracking_manager import PatchTrackingManager  # NEW: Tracks successful & failed patches

logger = logging.getLogger("TestRetryManager")
logger.setLevel(logging.DEBUG)


class TestRetryManager:
    """
    Manages test retries, patch application, and rollback if necessary.

    Features:
    - Tracks multiple failed patches per error.
    - Attempts multiple AI-generated patches before rolling back.
    - Stores successful patches in the learning DB.
    - Maintains a history of failed patches for later review.
    """

    MAX_PATCH_ATTEMPTS = 3  # Tries multiple AI patches before rollback

    def __init__(self):
        self.debugger_logger = DebuggerLogger()
        self.debugging_strategy = DebuggingStrategy()
        self.patch_tracker = PatchTrackingManager()  # NEW: Tracks failed and successful patches

    def run_tests(self) -> List[Dict[str, Any]]:
        """
        Runs tests and captures failures.
        """
        logger.info("🚀 Running tests...")
        result = subprocess.run(["pytest", "tests", "--disable-warnings"], capture_output=True, text=True)
        logger.debug(f"📝 Test Output:\n{result.stdout}")

        if result.returncode == 0:
            logger.info("✅ All tests passed! No debugging needed.")
            return []

        return self._parse_test_failures(result.stdout)

    def _parse_test_failures(self, test_output: str) -> List[Dict[str, Any]]:
        """
        Extracts failing test information.
        """
        failures = []
        for line in test_output.splitlines():
            if "FAILED" in line:
                parts = line.split(" - ")
                if len(parts) >= 2:
                    failures.append({
                        "file": parts[0].strip(),
                        "error": parts[1].strip()
                    })
        logger.info(f"⚠️ Found {len(failures)} failing tests.")
        return failures

    def retry_tests(self, max_retries: int = 3):
        """
        Runs tests, applies patches, retries fixes, and rolls back if all fail.
        """
        modified_files = []
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Debugging Attempt {attempt}/{max_retries}...")

            failures = self.run_tests()
            if not failures:
                logger.info("✅ All tests passed after debugging!")
                return {"status": "success", "message": "All tests passed!"}

            for failure in failures:
                file_name = failure["file"]
                error_message = failure["error"]
                error_sig = self.debugging_strategy._compute_error_signature(error_message, "")

                logger.info(f"🔧 Fixing {file_name} - Error: {error_message}")

                # Skip error if max patch attempts reached
                previous_fails = self.patch_tracker.get_failed_patches(error_sig)
                if len(previous_fails) >= self.MAX_PATCH_ATTEMPTS:
                    logger.warning(f"🚨 Max patch attempts reached for error: {error_sig}. Skipping further attempts.")
                    continue

                # Try multiple patches for the same issue before rollback
                patch_attempts = 0
                while patch_attempts < self.MAX_PATCH_ATTEMPTS:
                    patch = self.debugging_strategy.generate_patch(error_message, "", file_name)

                    if not patch:
                        logger.warning(f"❌ No patch generated for {file_name}. Skipping.")
                        break

                    logger.info(f"🛠️ Attempting patch {patch_attempts + 1} for {file_name}...")
                    patch_success = self.debugging_strategy.apply_patch(patch)

                    if patch_success:
                        modified_files.append(file_name)
                        logger.info(f"✅ Patch applied successfully for {file_name}")
                        self.patch_tracker.record_successful_patch(error_sig, patch)
                        self.debugging_strategy.learning_db[error_sig] = {"patch": patch, "success": True}
                        self.debugging_strategy._save_learning_db()
                        break  # Exit loop since patch worked
                    else:
                        logger.warning(f"❌ Patch failed for {file_name}")
                        self.patch_tracker.record_failed_patch(error_sig, patch)
                        patch_attempts += 1

                if patch_attempts >= self.MAX_PATCH_ATTEMPTS:
                    logger.error(f"❌ Could not fix {file_name} after multiple attempts. Rolling back.")
                    self.rollback_changes(modified_files)
                    return {"status": "error", "message": f"Could not fix {file_name} automatically."}

        logger.error("🛑 Max retries reached. Debugging unsuccessful.")
        return {"status": "error", "message": "Max retries reached. Debugging failed."}

    def rollback_changes(self, modified_files: List[str]):
        """
        Rolls back changes if debugging fails.
        """
        if not modified_files:
            logger.info("No files modified, nothing to rollback.")
            return

        for file in modified_files:
            backup_path = f"{file}.backup"
            if os.path.exists(backup_path):
                shutil.copy(backup_path, file)
                logger.info(f"🔄 Rolled back {file} from backup.")


if __name__ == "__main__":
    manager = TestRetryManager()
    manager.retry_tests(max_retries=3)
