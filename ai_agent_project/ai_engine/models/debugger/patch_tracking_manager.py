"""
This Python module allows for tracking of debugging patches added to AI models.
It includes functionalities for:
  - Recording failed patches to avoid duplicate attempts.
  - Logging successful patches.
  - Tracking applied patches.
  - Managing import fixes.
  - Storing AI-generated feedback.
  - Tracking daily AI performance metrics.
  - Retrieving failed or successful patches.
  - Rolling back (undoing) the last applied fix.
  
Usage:
    Instantiate the PatchTrackingManager and use its methods to record patch attempts,
    analyze performance, manage applied patches, and perform rollback operations.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("PatchTrackingManager")
logger.setLevel(logging.DEBUG)

class PatchTrackingManager:
    """
    Manages AI debugging patch tracking, including:
      - Failed patches
      - Successful patches
      - Applied patches
      - Import fixes tracking
      - AI feedback storage
      - AI performance analytics
    """

    def __init__(self):
        """Initialize patch tracking with persistent storage."""
        self.PATCH_STORAGE_DIR = "patch_data"
        os.makedirs(self.PATCH_STORAGE_DIR, exist_ok=True)

        # File paths for different tracking data
        self.FAILED_PATCHES_FILE = os.path.join(self.PATCH_STORAGE_DIR, "failed_patches.json")
        self.SUCCESSFUL_PATCHES_FILE = os.path.join(self.PATCH_STORAGE_DIR, "successful_patches.json")
        self.APPLIED_PATCHES_FILE = os.path.join(self.PATCH_STORAGE_DIR, "applied_patches.json")
        self.IMPORT_FIXES_FILE = os.path.join(self.PATCH_STORAGE_DIR, "import_fixes.json")
        self.AI_FEEDBACK_FILE = os.path.join(self.PATCH_STORAGE_DIR, "ai_feedback.json")
        self.AI_PERFORMANCE_FILE = os.path.join(self.PATCH_STORAGE_DIR, "ai_performance.json")

        # Load existing data or initialize empty dictionaries
        self.failed_patches = self._load_patch_data(self.FAILED_PATCHES_FILE, default={})
        self.successful_patches = self._load_patch_data(self.SUCCESSFUL_PATCHES_FILE, default={})
        self.applied_patches = self._load_patch_data(self.APPLIED_PATCHES_FILE, default={})
        self.import_fixes = self._load_patch_data(self.IMPORT_FIXES_FILE, default={})
        self.ai_feedback = self._load_patch_data(self.AI_FEEDBACK_FILE, default={})
        self.ai_performance = self._load_patch_data(self.AI_PERFORMANCE_FILE, default={})

    def _load_patch_data(self, file_path: str, default: Dict) -> Dict:
        """
        Loads JSON patch data from a file and ensures a dictionary is returned.

        Args:
            file_path (str): The file to load data from.
            default (dict): The default value to return if the file doesn't exist or is invalid.

        Returns:
            dict: The loaded patch data.
        """
        if not os.path.exists(file_path):
            return default

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                logger.warning(f"⚠️ Invalid format in {file_path}. Resetting data.")
                return default
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"⚠️ Error loading {file_path}: {e}. Resetting data.")
            return default

    def _save_patch_data(self, file_path: str, data: Dict):
        """
        Writes patch tracking data to a JSON file.

        Args:
            file_path (str): The file to write data to.
            data (dict): The data to write.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            logger.error(f"❌ Error saving {file_path}: {e}")

    # -------------------- Failed Patch Handling --------------------

    def record_failed_patch(self, error_signature: str, patch: str):
        """
        Records a failed patch for a specific error signature to avoid duplicate attempts.

        Args:
            error_signature (str): A unique signature for the error.
            patch (str): The patch content that failed.
        """
        self.failed_patches.setdefault(error_signature, [])
        if patch not in self.failed_patches[error_signature]:
            self.failed_patches[error_signature].append(patch)
            self._save_patch_data(self.FAILED_PATCHES_FILE, self.failed_patches)
            logger.warning(f"🔴 Failed patch recorded for error: {error_signature}")

    # -------------------- Successful Patch Handling --------------------

    def record_successful_patch(self, error_signature: str, patch: str):
        """
        Logs a successful patch for a specific error signature.

        Args:
            error_signature (str): A unique signature for the error.
            patch (str): The patch content that succeeded.
        """
        self.successful_patches.setdefault(error_signature, [])
        if patch not in self.successful_patches[error_signature]:
            self.successful_patches[error_signature].append(patch)
            self._save_patch_data(self.SUCCESSFUL_PATCHES_FILE, self.successful_patches)
            logger.info(f"🟢 Successful patch recorded for error: {error_signature}")

    # -------------------- Applied Patch Handling --------------------

    def record_applied_patch(self, error_signature: str, patch: str):
        """
        Logs an applied patch to track which patches were successfully used.

        Args:
            error_signature (str): A unique signature for the error.
            patch (str): The patch content that was applied.
        """
        self.applied_patches.setdefault(error_signature, [])
        if patch not in self.applied_patches[error_signature]:
            self.applied_patches[error_signature].append(patch)
            self._save_patch_data(self.APPLIED_PATCHES_FILE, self.applied_patches)
            logger.info(f"✅ Patch applied successfully for error: {error_signature}")

    # -------------------- Import Fix Tracking --------------------

    def record_import_fix(self, module_name: str, fix_success: bool):
        """
        Tracks the outcome of AI-generated import fixes.

        Args:
            module_name (str): The name of the module with the import issue.
            fix_success (bool): True if the fix was successful, False otherwise.
        """
        self.import_fixes.setdefault(module_name, {"fixed": 0, "failed": 0})
        if fix_success:
            self.import_fixes[module_name]["fixed"] += 1
            logger.info(f"✅ AI successfully fixed import issue: {module_name}")
        else:
            self.import_fixes[module_name]["failed"] += 1
            logger.warning(f"❌ AI failed to fix import issue: {module_name}")
        self._save_patch_data(self.IMPORT_FIXES_FILE, self.import_fixes)

    # -------------------- AI Feedback Handling --------------------

    def record_ai_feedback(self, error_signature: str, feedback: str, quality_score: int):
        """
        Stores AI-generated feedback on debugging effectiveness.

        Args:
            error_signature (str): The error signature associated with the feedback.
            feedback (str): The textual feedback.
            quality_score (int): A numerical score representing patch quality.
        """
        self.ai_feedback[error_signature] = {
            "feedback": feedback,
            "quality_score": quality_score
        }
        self._save_patch_data(self.AI_FEEDBACK_FILE, self.ai_feedback)
        logger.info(f"📊 AI Feedback Stored for {error_signature}: Score {quality_score}")

    # -------------------- AI Debugging Performance Analytics --------------------

    def track_ai_performance(self):
        """
        Tracks AI debugging performance by summarizing import fix success rates and AI feedback.
        The performance is logged daily.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        successful_fixes = sum(data.get("fixed", 0) for data in self.import_fixes.values())
        failed_fixes = sum(data.get("failed", 0) for data in self.import_fixes.values())
        total_fixes = successful_fixes + failed_fixes
        success_rate = round((successful_fixes / total_fixes * 100), 2) if total_fixes > 0 else 0

        self.ai_performance[today] = {
            "total_fixes": total_fixes,
            "success_rate": success_rate,
            "ai_feedback": {k: v.get("quality_score", 0) for k, v in self.ai_feedback.items()}
        }
        self._save_patch_data(self.AI_PERFORMANCE_FILE, self.ai_performance)
        logger.info(f"📈 AI Debugging Performance Updated for {today}: {self.ai_performance[today]}")

    # -------------------- Patch Retrieval & Rollback --------------------

    def get_failed_patches(self, error_signature: str) -> List[str]:
        """
        Retrieves failed patches for a specific error signature.

        Args:
            error_signature (str): The error signature to look up.

        Returns:
            List[str]: A list of failed patches.
        """
        return self.failed_patches.get(error_signature, [])

    def get_successful_patches(self, error_signature: str) -> List[str]:
        """
        Retrieves successful patches for a specific error signature.

        Args:
            error_signature (str): The error signature to look up.

        Returns:
            List[str]: A list of successful patches.
        """
        return self.successful_patches.get(error_signature, [])

    def undo_last_fix(self, error_signature: str) -> Optional[str]:
        """
        Rolls back the last successful patch for the given error signature.

        Args:
            error_signature (str): The error signature for which to roll back a patch.

        Returns:
            Optional[str]: The patch that was rolled back, or None if no patch exists.
        """
        if error_signature in self.successful_patches and self.successful_patches[error_signature]:
            last_patch = self.successful_patches[error_signature].pop()
            self._save_patch_data(self.SUCCESSFUL_PATCHES_FILE, self.successful_patches)
            logger.warning(f"🔄 Rolled back last fix for {error_signature}.")
            return last_patch
        else:
            logger.info(f"⚠️ No fix found to roll back for {error_signature}.")
            return None

    # -------------------- Patch Application --------------------

    def apply_patch(self, patch: str) -> bool:
        """
        Attempts to apply a given patch.
        For testing purposes, this stub simply returns True to indicate success.
        
        Args:
            patch (str): The patch string to apply.
            
        Returns:
            bool: True if the patch was "applied" successfully, False otherwise.
        """
        logger.debug(f"Applying patch:\n{patch}")
        # In a real implementation, integrate with a patching system.
        return True

if __name__ == "__main__":
    tracker = PatchTrackingManager()

    # Example Usage:
    tracker.record_failed_patch("error123", "--- old_code.py\n+++ new_code.py\n- old\n+ new")
    tracker.record_successful_patch("error123", "--- old_code.py\n+++ new_code.py\n- error\n+ fixed")
    tracker.record_applied_patch("error123", "--- old_code.py\n+++ new_code.py\n- error\n+ fixed")
    tracker.record_import_fix("numpy", True)
    tracker.record_ai_feedback("error123", "AI improved patch by refining logic.", 85)
    tracker.track_ai_performance()

    print("Failed patches for error123:", tracker.get_failed_patches("error123"))
    print("Successful patches for error123:", tracker.get_successful_patches("error123"))
    print("Applied patches for error123:", tracker.applied_patches.get("error123", []))
