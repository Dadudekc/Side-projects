"""
This module provides unit tests for the AIPatchReviewManager class which manages the automatic review, ranking, and application of code patches.

Test Cases:
- SetUp and TearDown: Configure the test environment before and after each test.
- test_rank_human_reviewed_patches: Check the AI's ability to rank human-reviewed patches based on evaluation criteria.
- test_log_patch_attempt: Ensure the module properly logs patch attempts with specified outcomes.
- test_get_best_patch: Verify retrieval of the highest-ranked patch.
- test_process_human_reviewed_patches_success: Ensure that when patch application succeeds, the outcome is logged correctly.
- test_process_human_reviewed_patches_failure: Ensure that when patch application fails, the outcome is logged correctly.
- test_analyze_patch_failures: Confirm that common failure patterns are correctly analyzed.
"""

import json
import os
import unittest
from unittest.mock import patch

from ai_engine.patch_review_manager import (
    DETAILED_ERROR_LOG_FILE,
    HUMAN_REVIEW_FILE,
    PATCH_RANKINGS_FILE,
    AIPatchReviewManager,
)
from agents.core.utilities.ai_client import AIClient
# Updated import: use the full module path for patch tracking manager.
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

class TestAIPatchReviewManager(unittest.TestCase):
    """Unit tests for the AIPatchReviewManager class."""

    def setUp(self):
        """Sets up an instance of AIPatchReviewManager for testing."""
        self.manager = AIPatchReviewManager()
        self.error_signature = "example_error_signature"
        self.test_patch = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ fixed code"""

    def tearDown(self):
        """Cleanup after tests by removing any created test files."""
        for file in [HUMAN_REVIEW_FILE, PATCH_RANKINGS_FILE, DETAILED_ERROR_LOG_FILE]:
            if os.path.exists(file):
                os.remove(file)

    @patch("agents.core.utilities.ai_client.AIClient.evaluate_patch_with_reason")
    def test_rank_human_reviewed_patches(self, mock_evaluate_patch):
        """Test AI ranking of human-reviewed patches."""
        # Simulate a consistent evaluation from AIClient
        mock_evaluate_patch.side_effect = lambda patch: {"score": 0.8, "reason": "Good fix"}

        # Set up human review data with two patches for the error signature
        self.manager.human_review = {
            self.error_signature: [
                self.test_patch,
                """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ better fix"""
            ]
        }

        self.manager.rank_human_reviewed_patches()
        self.assertIn(self.error_signature, self.manager.patch_rankings)
        self.assertGreater(len(self.manager.patch_rankings[self.error_signature]), 0)

    def test_log_patch_attempt(self):
        """Test logging of patch attempts."""
        self.manager.log_patch_attempt(
            self.error_signature, self.test_patch, "Applied Successfully", "Fixed import issue"
        )

        with open(DETAILED_ERROR_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

        self.assertIn(self.error_signature, logs)
        self.assertEqual(logs[self.error_signature][0]["outcome"], "Applied Successfully")

    def test_get_best_patch(self):
        """Test retrieving the highest-ranked patch."""
        self.manager.patch_rankings = {self.error_signature: [self.test_patch]}
        best_patch = self.manager.get_best_patch(self.error_signature)
        self.assertEqual(best_patch, self.test_patch)

    @patch("ai_engine.patch_review_manager.AIPatchReviewManager.rank_human_reviewed_patches")
    @patch("ai_engine.models.debugger.patch_tracking_manager.PatchTrackingManager.apply_patch", return_value=True)
    def test_process_human_reviewed_patches_success(self, mock_apply_patch, mock_rank_patches):
        """Test processing of human-reviewed patches when application succeeds."""
        self.manager.patch_rankings = {self.error_signature: [self.test_patch]}
        self.manager.process_human_reviewed_patches()

        with open(DETAILED_ERROR_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

        self.assertIn(self.error_signature, logs)
        self.assertEqual(logs[self.error_signature][0]["outcome"], "Applied Successfully")

    @patch("ai_engine.patch_review_manager.AIPatchReviewManager.rank_human_reviewed_patches")
    @patch("ai_engine.models.debugger.patch_tracking_manager.PatchTrackingManager.apply_patch", return_value=False)
    def test_process_human_reviewed_patches_failure(self, mock_apply_patch, mock_rank_patches):
        """Test processing of human-reviewed patches when application fails."""
        self.manager.patch_rankings = {self.error_signature: [self.test_patch]}
        self.manager.process_human_reviewed_patches()

        with open(DETAILED_ERROR_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

        self.assertIn(self.error_signature, logs)
        self.assertEqual(logs[self.error_signature][0]["outcome"], "Failed to Apply")

    def test_analyze_patch_failures(self):
        """Test analysis of common patch failure patterns."""
        self.manager.detailed_logs = {
            self.error_signature: [
                {"patch": self.test_patch, "outcome": "Failed to Apply", "extra_info": "Syntax error"},
                {"patch": self.test_patch, "outcome": "Failed to Apply", "extra_info": "Import missing"},
            ]
        }

        failure_patterns = self.manager.analyze_patch_failures()
        self.assertIn("Syntax error", failure_patterns[self.error_signature])
        self.assertIn("Import missing", failure_patterns[self.error_signature])


if __name__ == "__main__":
    unittest.main()
