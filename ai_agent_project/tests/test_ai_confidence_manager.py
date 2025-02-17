import json
import os
import unittest
from unittest.mock import MagicMock, patch

from ai_engine.confidence_manager import (
    AI_CONFIDENCE_FILE, PATCH_HISTORY_FILE, AIConfidenceManager
)


class TestAIConfidenceManager(unittest.TestCase):
    """Unit tests for the AIConfidenceManager class."""

    def setUp(self):
        """Sets up an instance of AIConfidenceManager for testing."""
        self.manager = AIConfidenceManager()
        self.error_signature = "example_error_signature"
        self.test_patch = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ fixed code"""

    def tearDown(self):
        """Cleanup after tests by removing AI confidence and patch history files if created."""
        for file in [AI_CONFIDENCE_FILE, PATCH_HISTORY_FILE]:
            if os.path.exists(file):
                os.remove(file)

    @patch("random.uniform", return_value=0.8)
    def test_assign_confidence_score(self, mock_random):
        """Test assigning confidence scores and storing them."""
        score, reason = self.manager.assign_confidence_score(self.error_signature, self.test_patch)
        self.assertGreaterEqual(score, 0.1)
        self.assertLessEqual(score, 1.0)

        with open(AI_CONFIDENCE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn(self.error_signature, data)
        self.assertEqual(data[self.error_signature][0]["patch"], self.test_patch)

    @patch("agents.core.utilities.ai_confidence_manager.AIConfidenceManager._get_historical_success_rate", return_value=0.9)
    def test_assign_confidence_high_success(self, mock_success_rate):
        """Test that a high historical success rate results in high confidence scores."""
        score, _ = self.manager.assign_confidence_score(self.error_signature, self.test_patch)
        self.assertGreater(score, 0.7)

    def test_get_best_high_confidence_patch(self):
        """Test retrieving the best high-confidence patch."""
        self.manager.confidence_scores[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.6, "reason": "Medium confidence"},
            {"patch": "patch2", "confidence": 0.9, "reason": "Highly similar to past fix"},
        ]
        best_patch = self.manager.get_best_high_confidence_patch(self.error_signature)
        self.assertEqual(best_patch, "patch2")

    def test_get_best_high_confidence_patch_none(self):
        """Test that no patch is returned if all confidence scores are too low."""
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
        """Test that no reattempt is suggested if confidence is still too low."""
        self.manager.confidence_scores[self.error_signature] = [
            {"patch": "patch1", "confidence": 0.6, "reason": "Confidence still low"},
        ]
        self.manager.patch_history[self.error_signature] = ["patch1"]

        suggested_patch = self.manager.suggest_patch_reattempt(self.error_signature)
        self.assertIsNone(suggested_patch)


if __name__ == "__main__":
    unittest.main()