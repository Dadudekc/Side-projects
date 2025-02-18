"""

This snippet of code includes a class named PatchTrackingManager that manages AI debugging patch tracking. The class includes methods to load and save patch data, handle successful and failed patches, track import fixes, handle AI feedback, track AI debugging performance, and review and rollback fixes.

The patch storage, including failed and successful patches, import fixes, AI feedback, and performance data, is stored in JSON files. Debugging events are logged.

There is a demonstration of how the PatchTrackingManager is used,
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Union

logger = logging.getLogger("PatchTrackingManager")
logger.setLevel(logging.DEBUG)

# Constants for Patch Storage
PATCH_STORAGE_DIR = "patch_data"
os.makedirs(PATCH_STORAGE_DIR, exist_ok=True)

FAILED_PATCHES_FILE = os.path.join(PATCH_STORAGE_DIR, "failed_patches.json")
SUCCESSFUL_PATCHES_FILE = os.path.join(PATCH_STORAGE_DIR, "successful_patches.json")
IMPORT_FIXES_FILE = os.path.join(PATCH_STORAGE_DIR, "import_fixes.json")
AI_FEEDBACK_FILE = os.path.join(PATCH_STORAGE_DIR, "ai_feedback.json")
AI_PERFORMANCE_FILE = os.path.join(PATCH_STORAGE_DIR, "ai_performance.json")


class PatchTrackingManager:
    """
    Manages AI debugging patch tracking, including:
    - Failed patches
    - Successful patches
    - Import fixes tracking
    - AI feedback storage
    - AI performance analytics
    """

    def __init__(self):
        """Initialize patch tracking with persistent storage."""
        self.failed_patches = self._load_patch_data(FAILED_PATCHES_FILE, default={})
        self.successful_patches = self._load_patch_data(SUCCESSFUL_PATCHES_FILE, default={})
        self.import_fixes = self._load_patch_data(IMPORT_FIXES_FILE, default={})
        self.ai_feedback = self._load_patch_data(AI_FEEDBACK_FILE, default={})
        self.ai_performance = self._load_patch_data(AI_PERFORMANCE_FILE, default={})

    def _load_patch_data(self, file_path: str, default: Dict) -> Dict:
        """Loads JSON patch data, ensuring valid dictionary format."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):  
                        return data  # ✅ Valid dictionary
                    else:
                        logger.warning(f"⚠️ Invalid format in {file_path}. Resetting.")
                        return default  # 🔄 Reset corrupted structure
            except json.JSONDecodeError:
                logger.error(f"⚠️ Corrupt JSON detected in {file_path}. Resetting.")
                return default
        return default

    def _save_patch_data(self, file_path: str, data: Dict):
        """Safely writes patch tracking data to a JSON file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Error saving {file_path}: {e}")

    # ✅ **Failed Patch Handling**
    def record_failed_patch(self, error_signature: str, patch: str):
        """Records a failed patch, preventing duplicate entries."""
        self.failed_patches.setdefault(error_signature, [])
        if patch not in self.failed_patches[error_signature]:  
            self.failed_patches[error_signature].append(patch)
            self._save_patch_data(FAILED_PATCHES_FILE, self.failed_patches)
            logger.warning(f"🔴 Failed patch recorded for error: {error_signature}")

    # ✅ **Successful Patch Handling**
    def record_successful_patch(self, error_signature: str, patch: str):
        """Logs a successful patch to track AI debugging progress."""
        self.successful_patches.setdefault(error_signature, [])
        if patch not in self.successful_patches[error_signature]:
            self.successful_patches[error_signature].append(patch)
            self._save_patch_data(SUCCESSFUL_PATCHES_FILE, self.successful_patches)
            logger.info(f"🟢 Successful patch recorded for error: {error_signature}")

    # ✅ **Import Fix Tracking**
    def record_import_fix(self, module_name: str, fix_success: bool):
        """Tracks AI-generated import fixes separately to assess performance."""
        self.import_fixes.setdefault(module_name, {"fixed": 0, "failed": 0})

        if fix_success:
            self.import_fixes[module_name]["fixed"] += 1
            logger.info(f"✅ AI successfully fixed import issue: {module_name}")
        else:
            self.import_fixes[module_name]["failed"] += 1
            logger.warning(f"❌ AI failed to fix import issue: {module_name}")

        self._save_patch_data(IMPORT_FIXES_FILE, self.import_fixes)

    # ✅ **AI Feedback Handling**
    def record_ai_feedback(self, error_signature: str, feedback: str, quality_score: int):
        """Stores AI-generated feedback on debugging effectiveness."""
        self.ai_feedback[error_signature] = {
            "feedback": feedback,
            "quality_score": quality_score
        }
        self._save_patch_data(AI_FEEDBACK_FILE, self.ai_feedback)
        logger.info(f"📊 AI Feedback Stored: {error_signature} -> Score: {quality_score}")

    # ✅ **AI Debugging Performance Analytics**
    def track_ai_performance(self):
        """Tracks AI debugging success rates and import fix performance."""
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

        self._save_patch_data(AI_PERFORMANCE_FILE, self.ai_performance)
        logger.info(f"📈 AI Debugging Performance Updated: {self.ai_performance[today]}")

    # ✅ **Review & Rollback**
    def get_failed_patches(self, error_signature: str) -> List[str]:
        """Retrieves failed patches for a specific error."""
        return self.failed_patches.get(error_signature, [])

    def get_successful_patches(self, error_signature: str) -> List[str]:
        """Retrieves successful patches for a specific error."""
        return self.successful_patches.get(error_signature, [])

    def undo_last_fix(self, error_signature: str):
        """Rolls back the last fix for a given error signature."""
        if error_signature in self.successful_patches and self.successful_patches[error_signature]:
            last_patch = self.successful_patches[error_signature].pop()
            self._save_patch_data(SUCCESSFUL_PATCHES_FILE, self.successful_patches)
            logger.warning(f"🔄 Rolled back last fix for {error_signature}. Patch removed.")
            return last_patch
        else:
            logger.info(f"⚠️ No fix found to roll back for {error_signature}.")
            return None


if __name__ == "__main__":
    tracker = PatchTrackingManager()

    # Example Usage
    tracker.record_failed_patch("error123", "--- old_code.py\n+++ new_code.py\n- old\n+ new")
    tracker.record_successful_patch("error123", "--- old_code.py\n+++ new_code.py\n- error\n+ fixed")
    tracker.record_import_fix("numpy", True)
    tracker.record_ai_feedback("error123", "AI improved patch by refining logic.", 85)
    tracker.track_ai_performance()

    print(tracker.get_failed_patches("error123"))
    print(tracker.get_successful_patches("error123"))
