import os
import shutil
import subprocess
import logging
import re
from typing import Dict, Any, List
from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

logger = logging.getLogger("AutoFixManager")
logger.setLevel(logging.DEBUG)


class AutoFixManager:
    """
    Handles automated test retries, patching failed tests, and rollback if necessary.
    
    Features:
    - Tracks multiple failed patches per error.
    - Attempts multiple AI-generated patches before rollback.
    - Stores successful patches in the learning DB.
    - Maintains a history of failed patches for later review.
    """

    MAX_PATCH_ATTEMPTS = 3  # Tries multiple AI patches before rollback

    def __init__(self):
        self.debugging_strategy = DebuggingStrategy()
        self.patch_tracker = PatchTrackingManager()

    def run_tests(self) -> List[Dict[str, Any]]:
        """
        Runs tests and captures failures.

        Returns:
            List[Dict[str, Any]]: A list of failed test cases with file paths and errors.
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
        Extracts failing test information from pytest output.

        Args:
            test_output (str): The output log from pytest.

        Returns:
            List[Dict[str, Any]]: Extracted failure details.
        """
        failures = []
        failure_pattern = re.compile(r"FAILED (\S+) - (.+)")

        # ✅ Convert bytes to string if necessary
        if isinstance(test_output, bytes):
            test_output = test_output.decode("utf-8")  

        for match in failure_pattern.findall(test_output):
            file, error_message = match
            failures.append({"file": file.strip(), "error": error_message.strip()})

        logger.info(f"⚠️ Found {len(failures)} failing tests.")
        return failures

    def retry_tests(self, max_retries: int = 3):
        """
        Runs tests, applies patches, retries fixes, and rolls back if all fail.

        Args:
            max_retries (int): Maximum number of retries before rollback.

        Returns:
            Dict[str, Any]: Final retry status.
        """
        modified_files = set()  # ✅ Track modified files
        failed_files = set()  # ✅ Track files that still fail after all attempts

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

                # Skip file if max patch attempts reached
                previous_fails = self.patch_tracker.get_failed_patches(error_sig)
                if len(previous_fails) >= self.MAX_PATCH_ATTEMPTS:
                    logger.warning(f"🚨 Max patch attempts reached for {file_name}. Skipping further attempts.")
                    failed_files.add(file_name)
                    continue

                # Attempt multiple patches per file
                patch_attempts = 0
                while patch_attempts < self.MAX_PATCH_ATTEMPTS:
                    patch = self.debugging_strategy.generate_patch(error_message, "", file_name)

                    if not patch:
                        logger.warning(f"❌ No patch generated for {file_name}. Skipping.")
                        failed_files.add(file_name)
                        break

                    logger.info(f"🛠️ Attempting patch {patch_attempts + 1}/{self.MAX_PATCH_ATTEMPTS} for {file_name}...")
                    patch_success = self.debugging_strategy.apply_patch(patch)

                    if patch_success:
                        modified_files.add(file_name)
                        logger.info(f"✅ Patch applied successfully for {file_name}")
                        self.patch_tracker.record_successful_patch(error_sig, patch)
                        self.debugging_strategy.learning_db[error_sig] = {"patch": patch, "success": True}
                        self.debugging_strategy._save_learning_db()
                        break  # ✅ Stop trying more patches since this one worked
                    else:
                        logger.warning(f"❌ Patch failed for {file_name}")
                        self.patch_tracker.record_failed_patch(error_sig, patch)
                        patch_attempts += 1

                if patch_attempts >= self.MAX_PATCH_ATTEMPTS:
                    logger.error(f"❌ Could not fix {file_name} after multiple attempts.")
                    failed_files.add(file_name)

        # ✅ Only roll back files that still fail, keeping successful patches
        if failed_files:
            logger.error(f"🛑 Rolling back changes for failed files: {failed_files}")
            self.rollback_changes(failed_files)

        # ✅ If no files failed, debugging was successful
        if not failed_files:
            return {"status": "success", "message": "All failing tests were fixed!"}

        return {"status": "error", "message": "Max retries reached. Debugging failed."}

    def rollback_changes(self, modified_files: List[str]):
        """
        Rolls back changes if debugging fails.

        Args:
            modified_files (List[str]): List of modified files to be restored.
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
    manager = AutoFixManager()
    manager.retry_tests(max_retries=3)
