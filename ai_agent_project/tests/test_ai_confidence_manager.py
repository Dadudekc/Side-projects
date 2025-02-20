import json
import os
import unittest
from unittest.mock import patch

# Ensure correct import paths
from ai_engine.confidence_manager import (
    AI_CONFIDENCE_FILE,
    PATCH_HISTORY_FILE,
    CONFIDENCE_DB,
    AIConfidenceManager
)

class TestAIConfidenceManager(unittest.TestCase):
    """Unit tests for the AIConfidenceManager class."""

    def setUp(self):
        """Initialize the AIConfidenceManager instance and test data."""
        self.manager = AIConfidenceManager()
        self.error_signature = "test_error_signature"
        self.test_patch = (
            "--- a/code.py\n+++ b/code.py\n@@ -1 +1 @@\n- old code\n+ fixed code"
        )
        # Ensure internal stores start empty
        self.manager.confidence_scores = {}
        self.manager.patch_history = {}
        self.manager.high_confidence_store = {}

    def tearDown(self):
        """Clean up generated JSON files to avoid interference between tests."""
        for file in [AI_CONFIDENCE_FILE, PATCH_HISTORY_FILE, CONFIDENCE_DB]:
            if os.path.exists(file):
                os.remove(file)

    @patch("random.uniform", return_value=0.8)  # Control randomness
    @patch.object(AIConfidenceManager, "_get_historical_success_rate", return_value=0.7)
    def test_assign_confidence_score(self, mock_history, mock_random):
        """
        Test that assign_confidence_score assigns the expected confidence score and reason,
        and that it correctly stores the patch in both confidence_scores and high_confidence_store.
        """
        score, reason = self.manager.assign_confidence_score(self.error_signature, self.test_patch)

        # Given historical success=0.7 and random.uniform=0.8, our calculation:
        # confidence_score = max(0.1, min(1.0, 0.7 + 0.1)) = 0.8
        self.assertAlmostEqual(score, 0.8, places=7)

        # With a score of 0.8 (>=0.75), the reason should be the high-confidence message.
        self.assertEqual(reason, "Highly similar to a past fix with high success.")

        # Check that the confidence_scores store has the patch entry.
        self.assertIn(self.error_signature, self.manager.confidence_scores)
        entry = self.manager.confidence_scores[self.error_signature][0]
        self.assertEqual(entry["patch"], self.test_patch)
        self.assertAlmostEqual(entry["confidence"], 0.8, places=7)
        self.assertEqual(entry["reason"], "Highly similar to a past fix with high success.")

        # Since score>=0.75, it should also be stored in high_confidence_store.
        self.assertIn(self.error_signature, self.manager.high_confidence_store)
        high_entry = self.manager.high_confidence_store[self.error_signature][0]
        self.assertEqual(high_entry["patch"], self.test_patch)
        self.assertAlmostEqual(high_entry["confidence"], 0.8, places=7)

        # Additionally, the updated confidence data should have been saved to disk.
        with open(AI_CONFIDENCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn(self.error_signature, data)
        self.assertEqual(data[self.error_signature][0]["patch"], self.test_patch)

    def test_get_best_high_confidence_patch(self):
        """
        Test retrieving the best high-confidence patch.
        """
        # Manually set the high_confidence_store for the error_signature.
        self.manager.high_confidence_store[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.65},
            {"patch": "patch2", "confidence": 0.9},
            {"patch": "patch3", "confidence": 0.8}
        ]
        best_patch = self.manager.get_best_high_confidence_patch(self.error_signature)
        self.assertEqual(best_patch, "patch2")

    def test_get_best_high_confidence_patch_none(self):
        """
        Test that None is returned when there are no high-confidence patches.
        """
        # Set an empty list for the error signature.
        self.manager.high_confidence_store[self.error_signature] = []
        best_patch = self.manager.get_best_high_confidence_patch(self.error_signature)
        self.assertIsNone(best_patch)

    def test_suggest_patch_reattempt(self):
        """
        Test suggesting a patch for reattempt when a stored patch has improved confidence.
        """
        # Set up a confidence_scores store with one high-confidence and one lower patch.
        self.manager.confidence_scores[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.75, "reason": "High confidence"},
            {"patch": "patch2", "confidence": 0.5, "reason": "Low confidence"}
        ]
        # Also, record these patches in patch_history.
        self.manager.patch_history[self.error_signature] = ["patch1", "patch2"]

        suggested_patch = self.manager.suggest_patch_reattempt(self.error_signature)
        self.assertEqual(suggested_patch, "patch1")

    def test_suggest_patch_reattempt_none(self):
        """
        Test that suggest_patch_reattempt returns None when no patch qualifies.
        """
        # Setup a scenario where no patch reaches high confidence.
        self.manager.confidence_scores[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.65, "reason": "Medium confidence"}
        ]
        self.manager.patch_history[self.error_signature] = ["patch1"]

        suggested_patch = self.manager.suggest_patch_reattempt(self.error_signature)
        self.assertIsNone(suggested_patch)

if __name__ == "__main__":
    unittest.main()
