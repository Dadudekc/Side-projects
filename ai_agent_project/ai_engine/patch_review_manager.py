"""
This module provides the AIPatchReviewManager class which manages the automatic review,
ranking, and application of code patches.

Features:
  - Uses AI to rank patches by effectiveness based on past success rates.
  - Logs every patch attempt with AI reasoning and human feedback.
  - Tracks which patches worked and refines AI decision-making over time.
"""

import json
import os
import logging
from typing import Dict, List, Optional

from agents.core.utilities.ai_client import AIClient
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

logger = logging.getLogger("AIPatchReviewManager")
logger.setLevel(logging.DEBUG)

# File path constants
HUMAN_REVIEW_FILE = "human_review.json"
PATCH_HISTORY_FILE = "patch_history.json"
AI_DECISIONS_LOG = "ai_decisions.json"
PATCH_RANKINGS_FILE = "patch_rankings.json"
DETAILED_ERROR_LOG_FILE = "detailed_patch_log.json"

class AIPatchReviewManager:
    """
    Manages the automatic review, ranking, and application of code patches.

    Attributes:
      human_review (dict): A mapping of error signatures to lists of human-reviewed patches.
      patch_rankings (dict): A mapping of error signatures to lists of patches ranked by quality.
      detailed_logs (dict): Detailed log entries for each patch attempt.
      patch_tracker (PatchTrackingManager): Manages patch application attempts.
      ai_client (AIClient): The AI client used for evaluating patches.
    """
    def __init__(self):
        self.patch_tracker = PatchTrackingManager()
        self.ai_client = AIClient()
        self.human_review: Dict[str, List[str]] = self._load_patch_data(HUMAN_REVIEW_FILE)
        self.patch_history: Dict[str, List[dict]] = self._load_patch_data(PATCH_HISTORY_FILE)
        self.ai_decisions: Dict[str, List[dict]] = self._load_patch_data(AI_DECISIONS_LOG)
        self.patch_rankings: Dict[str, List[str]] = self._load_patch_data(PATCH_RANKINGS_FILE)
        self.detailed_logs: Dict[str, List[dict]] = self._load_patch_data(DETAILED_ERROR_LOG_FILE)

    def _load_patch_data(self, file_path: str) -> Dict[str, List[dict]]:
        """Loads patch tracking data from a JSON file."""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load {file_path}: {e}")
        return {}

    def _save_patch_data(self, file_path: str, data: Dict[str, List[dict]]):
        """Saves patch tracking data to a JSON file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Failed to save {file_path}: {e}")

    def rank_human_reviewed_patches(self):
        """Ranks human-reviewed patches based on AI evaluation and past success rates."""
        ranked_patches = {}

        for error_signature, patches in self.human_review.items():
            patch_scores = []

            for patch in patches:
                evaluation = self.ai_client.evaluate_patch_with_reason(patch)
                patch_score = evaluation["score"]
                decision_reason = evaluation["reason"]

                # Log AI decision reasoning
                self.ai_decisions.setdefault(error_signature, []).append({
                    "patch": patch,
                    "score": patch_score,
                    "reason": decision_reason
                })

                patch_scores.append((patch_score, patch))

            # Sort patches in descending order by score
            patch_scores.sort(key=lambda x: x[0], reverse=True)
            ranked_patches[error_signature] = [patch for score, patch in patch_scores]

        self.patch_rankings = ranked_patches
        self._save_patch_data(PATCH_RANKINGS_FILE, self.patch_rankings)
        logger.info("📊 AI-ranked human-reviewed patches saved.")

    def log_patch_attempt(self, error_signature: str, patch: str, outcome: str, extra_info: Optional[str] = None):
        """
        Logs a patch attempt with outcome and additional information.
        """
        log_entry = {
            "patch": patch,
            "outcome": outcome,
            "extra_info": extra_info
        }
        self.detailed_logs.setdefault(error_signature, []).append(log_entry)
        self._save_patch_data(DETAILED_ERROR_LOG_FILE, self.detailed_logs)
        logger.info(f"📝 Logged patch attempt for {error_signature}: {outcome}")

    def get_best_patch(self, error_signature: str) -> Optional[str]:
        """
        Retrieves the highest-ranked patch for a given error signature.
        """
        patches = self.patch_rankings.get(error_signature, [])
        if patches:
            return patches[0]
        return None

    def process_human_reviewed_patches(self):
        """
        Processes human-reviewed patches: ranks them, applies the best patch via PatchTrackingManager,
        and logs the outcome.
        """
        self.rank_human_reviewed_patches()
        for error_signature, patches in self.patch_rankings.items():
            if patches:
                best_patch = patches[0]
                applied = self.patch_tracker.apply_patch(best_patch)
                if applied:
                    self.log_patch_attempt(error_signature, best_patch, "Applied Successfully")
                else:
                    self.log_patch_attempt(error_signature, best_patch, "Failed to Apply", "Patch application error")

    def analyze_patch_failures(self) -> dict:
        """
        Analyzes detailed logs to extract common failure patterns.

        Returns:
            dict: Mapping of error signatures to failure reasons and counts.
        """
        failure_patterns = {}
        for error_signature, attempts in self.detailed_logs.items():
            pattern_counts = {}
            for entry in attempts:
                if entry["outcome"] == "Failed to Apply":
                    reason = entry.get("extra_info", "Unknown Failure")
                    pattern_counts[reason] = pattern_counts.get(reason, 0) + 1
            if pattern_counts:
                failure_patterns[error_signature] = pattern_counts
        logger.info(f"📉 Common Patch Failure Reasons: {failure_patterns}")
        return failure_patterns

if __name__ == "__main__":
    review_manager = AIPatchReviewManager()
    review_manager.process_human_reviewed_patches()
    review_manager.analyze_patch_failures()
