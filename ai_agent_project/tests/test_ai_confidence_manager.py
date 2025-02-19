"""
Unit tests for the AIConfidenceManager class.

This module tests the AIConfidenceManager's ability to:

- Assign and store confidence scores for code patches.
- Retrieve the best high-confidence patches.
- Suggest reattempts for patches based on improved confidence scores.
- Handle historical success rates effectively.

Each test initializes an AIConfidenceManager instance, runs assertions,
and cleans up any temporary files generated during the test.
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure correct import paths
from ai_engine.confidence_manager import (
    AI_CONFIDENCE_FILE, PATCH_HISTORY_FILE, AIConfidenceManager
)


class TestAIConfidenceManager(unittest.TestCase):
    """Unit tests for AIConfidenceManager."""

    def setUp(self):
        """Setup an AIConfidenceManager instance and mock data."""
        self.manager = AIConfidenceManager()
        self.error_signature = "example_error_signature"
        self.test_patch = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ fixed code"""

    def tearDown(self):
        """Clean up test files to ensure no leftover test data."""
        for file in [AI_CONFIDENCE_FILE, PATCH_HISTORY_FILE]:
            if os.path.exists(file):
                os.remove(file)

    @patch("random.uniform", return_value=0.8)  # Mocking confidence scores for consistency
    def test_assign_confidence_score(self, mock_random):
        """Test assigning confidence scores and storing them in AI_CONFIDENCE_FILE."""
        score, reason = self.manager.assign_confidence_score(self.error_signature, self.test_patch)

        # Ensure confidence score is within the expected range
        self.assertGreaterEqual(score, 0.1)
        self.assertLessEqual(score, 1.0)
        self.assertEqual(reason, "Confidence assigned based on history and AI analysis.")

        # Verify confidence data is saved correctly
        with open(AI_CONFIDENCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn(self.error_signature, data)
        self.assertEqual(data[self.error_signature][0]["patch"], self.test_patch)

    @patch("ai_engine.models.confidence_manager.AIConfidenceManager._get_historical_success_rate", return_value=0.9)
    def test_assign_confidence_high_success(self, mock_success_rate):
        """Test if a high historical success rate results in higher confidence scores."""
        score, _ = self.manager.assign_confidence_score(self.error_signature, self.test_patch)
        self.assertGreater(score, 0.7)

    def test_get_best_high_confidence_patch(self):
        """Test retrieving the best high-confidence patch from stored scores."""
        self.manager.confidence_scores[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.6, "reason": "Medium confidence"},
            {"patch": "patch2", "confidence": 0.9, "reason": "Highly similar to past fix"},
        ]
        best_patch = self.manager.get_best_high_confidence_patch(self.error_signature)
        self.assertEqual(best_patch, "patch2")

    def test_get_best_high_confidence_patch_none(self):
        """Test if no patch is returned when confidence scores are too low."""
        self.manager.confidence_scores[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.6, "reason": "Low confidence"},
        ]
        best_patch = self.manager.get_best_high_confidence_patch(self.error_signature)
        self.assertIsNone(best_patch)

    def test_suggest_patch_reattempt(self):
        """Test suggesting a reattempt for patches that initially failed but now have improved confidence."""
        self.manager.confidence_scores[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.8, "reason": "Confidence improved"},
            {"patch": "patch2", "confidence": 0.5, "reason": "Low confidence"},
        ]
        self.manager.patch_history[self.error_signature] = ["patch1"]

        suggested_patch = self.manager.suggest_patch_reattempt(self.error_signature)
        self.assertEqual(suggested_patch, "patch1")

    def test_suggest_patch_reattempt_none(self):
        """Test if no reattempt is suggested when confidence is still too low."""
        self.manager.confidence_scores[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.6, "reason": "Confidence still low"},
        ]
        self.manager.patch_history[self.error_signature] = ["patch1"]

        suggested_patch = self.manager.suggest_patch_reattempt(self.error_signature)
        self.assertIsNone(suggested_patch)


if __name__ == "__main__":
    unittest.main()
