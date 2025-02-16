import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("PatchTrackingManager")
logger.setLevel(logging.DEBUG)

# Constants for patch storage
FAILED_PATCHES_FILE = "failed_patches.json"
SUCCESSFUL_PATCHES_FILE = "successful_patches.json"
IMPORT_FIXES_FILE = "import_fixes.json"
AI_FEEDBACK_FILE = "ai_feedback.json"
AI_PERFORMANCE_FILE = "ai_performance.json"


class PatchTrackingManager:
    """
    **Tracks applied patches**, including:
    
    ✅ **Failed Patches:**  
        - Logs AI-generated patches that failed.  
        - Helps detect **recurring issues** & **bad AI fixes**.  
    
    ✅ **Successful Patches:**  
        - Stores patches that fixed errors.  
        - Can be used to train AI models & refine debugging strategies.  
    
    ✅ **Import Fixes Tracking:**  
        - **Separates import fixes** from other patches.  
        - **Tracks success/failure rates** for AI import corrections.  
    
    ✅ **AI Feedback Learning:**  
        - Stores **AI-generated feedback** on each patch.  
        - Helps AI **adjust debugging strategies** over time.  
    
    ✅ **Performance Analytics:**  
        - Tracks **AI debugging success rates over time**.  
        - Generates **import fix success rate reports**.  
    """

    def __init__(self):
        self.failed_patches = self._load_patch_data(FAILED_PATCHES_FILE)
        self.successful_patches = self._load_patch_data(SUCCESSFUL_PATCHES_FILE)
        self.import_fixes = self._load_patch_data(IMPORT_FIXES_FILE)
        self.ai_feedback = self._load_patch_data(AI_FEEDBACK_FILE)
        self.ai_performance = self._load_patch_data(AI_PERFORMANCE_FILE)

    def _load_patch_data(self, file_path: str) -> Dict[str, List[str]]:
        """Safely loads patch tracking data from a JSON file."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load {file_path}: {e}")
        return {}

    def _save_patch_data(self, file_path: str, data: Dict[str, List[str]]):
        """Safely saves patch tracking data to a JSON file with sorted entries."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump({k: sorted(set(v)) for k, v in data.items()}, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Failed to save {file_path}: {e}")

    # ✅ **Failed Patch Handling**
    def record_failed_patch(self, error_signature: str, patch: str):
        """Logs **failed** patch attempts. AI will analyze these failures later."""
        if error_signature not in self.failed_patches:
            self.failed_patches[error_signature] = []
        if patch not in self.failed_patches[error_signature]:  # Prevent duplicates
            self.failed_patches[error_signature].append(patch)
            self._save_patch_data(FAILED_PATCHES_FILE, self.failed_patches)
            logger.info(f"🔴 Stored failed patch for error: {error_signature}")

    # ✅ **Successful Patch Handling**
    def record_successful_patch(self, error_signature: str, patch: str):
        """Logs **successful** patches that AI can learn from."""
        if error_signature not in self.successful_patches:
            self.successful_patches[error_signature] = []
        if patch not in self.successful_patches[error_signature]:  # Prevent duplicates
            self.successful_patches[error_signature].append(patch)
            self._save_patch_data(SUCCESSFUL_PATCHES_FILE, self.successful_patches)
            logger.info(f"🟢 Stored successful patch for error: {error_signature}")

    # ✅ **Import Fix Tracking**
    def record_import_fix(self, module_name: str, fix_success: bool):
        """
        Tracks AI import fixes separately.
        📌 **Why?** Import errors are **common** but **easier to auto-fix**.
        """
        if module_name not in self.import_fixes:
            self.import_fixes[module_name] = {"fixed": 0, "failed": 0}

        if fix_success:
            self.import_fixes[module_name]["fixed"] += 1
            logger.info(f"✅ AI fixed import issue: {module_name}")
        else:
            self.import_fixes[module_name]["failed"] += 1
            logger.warning(f"❌ AI failed to fix import issue: {module_name}")

        self._save_patch_data(IMPORT_FIXES_FILE, self.import_fixes)

    # ✅ **AI Feedback Handling**
    def record_ai_feedback(self, error_signature: str, feedback: str, quality_score: int):
        """
        Logs AI feedback on patch quality.
        **Quality Score (0-100)**:
        - **90+** = Great Fix ✅
        - **50-89** = Acceptable 🤔
        - **Below 50** = AI needs improvement ❌
        """
        self.ai_feedback[error_signature] = {
            "feedback": feedback,
            "quality_score": quality_score
        }
        self._save_patch_data(AI_FEEDBACK_FILE, self.ai_feedback)
        logger.info(f"📊 AI Feedback Stored: {error_signature} -> Score: {quality_score}")

    # ✅ **AI Debugging Performance Analytics**
    def track_ai_performance(self):
        """
        Tracks **AI debugging success rates over time**.
        Generates **Import Fix Success Rate Reports** 📈.
        """
        today = datetime.now().strftime("%Y-%m-%d")
        successful_fixes = sum(data["fixed"] for data in self.import_fixes.values())
        failed_fixes = sum(data["failed"] for data in self.import_fixes.values())
        total_fixes = successful_fixes + failed_fixes
        success_rate = (successful_fixes / total_fixes * 100) if total_fixes > 0 else 0

        self.ai_performance[today] = {
            "total_fixes": total_fixes,
            "success_rate": round(success_rate, 2),
            "ai_feedback": {k: v["quality_score"] for k, v in self.ai_feedback.items()}
        }

        self._save_patch_data(AI_PERFORMANCE_FILE, self.ai_performance)
        logger.info(f"📈 AI Debugging Performance Updated: {self.ai_performance[today]}")

    # ✅ **Review & Rollback**
    def get_failed_patches(self, error_signature: str) -> List[str]:
        """Retrieves **failed patches** for a specific error (sorted)."""
        return sorted(set(self.failed_patches.get(error_signature, [])))

    def get_successful_patches(self, error_signature: str) -> List[str]:
        """Retrieves **successful patches** for a specific error (sorted)."""
        return sorted(set(self.successful_patches.get(error_signature, [])))

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
