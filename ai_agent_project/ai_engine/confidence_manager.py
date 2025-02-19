import json
import logging
import os
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger("AIConfidenceManager")
logger.setLevel(logging.DEBUG)

# Files for storing data
AI_CONFIDENCE_FILE = "ai_confidence_scores.json"
PATCH_HISTORY_FILE = "patch_history.json"
CONFIDENCE_DB = "confidence_store.json"

class AIConfidenceManager:
    """
    Manages AI confidence tracking for generated patches.
    - Loads historical patch data and AI confidence scores.
    - Assigns confidence scores using historical success rates.
    - Stores high-confidence patches separately to avoid redundant processing.
    - Provides methods to retrieve high-confidence patches and suggest patch re-attempts.
    """

    def __init__(self):
        self.confidence_scores = self._load_json(AI_CONFIDENCE_FILE)
        self.patch_history = self._load_json(PATCH_HISTORY_FILE)
        self.high_confidence_store = self._load_json(CONFIDENCE_DB)

    def _load_json(self, file_path: str) -> Dict:
        """Generic JSON loader."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"❌ Corrupted JSON file: {file_path}. Resetting to empty.")
                return {}
            except Exception as e:
                logger.error(f"❌ Failed to load {file_path}: {e}")
        return {}

    def _save_json(self, file_path: str, data: Dict):
        """Generic JSON saver."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Failed to save {file_path}: {e}")

    def _get_historical_success_rate(self, error_signature: str) -> float:
        """Calculates the success rate of past patches for this error."""
        patches = self.patch_history.get(error_signature, [])
        if not patches:
            return 0.5  # Default confidence if no history exists
        success_count = sum(1 for p in patches if isinstance(p, dict) and p.get("outcome") == "Applied Successfully")
        return round(success_count / len(patches), 2)

    def calculate_confidence(self, error_signature: str) -> float:
        """
        Returns the confidence level for a given error signature.
        """
        return self.confidence_scores.get(error_signature, 0.5)

    def assign_confidence_score(self, error_signature: str, patch: str) -> Tuple[float, str]:
        """
        Assigns a confidence score to the given patch.
        """
        historical_success = self._get_historical_success_rate(error_signature)
        confidence_score = max(0.1, min(1.0, historical_success + 0.1))  # Ensure between 0.1 and 1.0

        # Reasoning logic
        if confidence_score >= 0.75:
            reason = "Highly similar to a past fix with high success."
        elif confidence_score >= 0.5:
            reason = "Patch structure matches known patterns, medium confidence."
        else:
            reason = "New approach detected, uncertain outcome."

        # Store confidence score
        self.confidence_scores.setdefault(error_signature, []).append({
            "patch": patch,
            "confidence": confidence_score,
            "reason": reason
        })

        # Save the updated confidence data
        self._save_json(AI_CONFIDENCE_FILE, self.confidence_scores)

        return confidence_score, reason

    def get_best_high_confidence_patch(self, error_signature: str) -> Optional[str]:
        """
        Retrieves the best high-confidence patch.
        """
        patches = self.confidence_scores.get(error_signature, [])
        valid_patches = [p for p in patches if isinstance(p, dict) and "confidence" in p]

        if not valid_patches:
            return None

        best_patch = max(valid_patches, key=lambda p: p["confidence"], default=None)
        return best_patch["patch"] if best_patch and best_patch["confidence"] >= 0.75 else None

    def suggest_patch_reattempt(self, error_signature: str) -> Optional[str]:
        """
        Suggests a patch for reattempt if it now has improved confidence.
        """
        patches = self.confidence_scores.get(error_signature, [])
        valid_patches = [p for p in patches if isinstance(p, dict) and "confidence" in p]

        for patch_entry in valid_patches:
            if patch_entry["confidence"] >= 0.75 and patch_entry["patch"] in self.patch_history.get(error_signature, []):
                return patch_entry["patch"]

        return None

if __name__ == "__main__":
    manager = AIConfidenceManager()
    test_error = "example_error_signature"
    test_patch = (
        "--- a/code.py\n+++ b/code.py\n@@ -1 +1 @@\n- old code\n+ fixed code"
    )

    score, reason = manager.assign_confidence_score(test_error, test_patch)
    logger.info(f"🎯 Assigned confidence score: {score}, Reason: {reason}")

    best_patch = manager.get_best_high_confidence_patch(test_error)
    if best_patch:
        logger.info(f"🚀 Best high-confidence patch suggested: {best_patch}")
    
    reattempt_patch = manager.suggest_patch_reattempt(test_error)
    if reattempt_patch:
        logger.info(f"🔄 AI suggests retrying: {reattempt_patch}")
