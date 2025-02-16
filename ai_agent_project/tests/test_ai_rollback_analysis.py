import json
import os
import unittest
from unittest.mock import MagicMock, patch

from agents.core.utilities.ai_rollback_analysis import (
    AI_DECISIONS_LOG,
    FAILED_PATCHES_FILE,
    HUMAN_REVIEW_FILE,
    PATCH_HISTORY_FILE,
    REFINED_PATCHES_FILE,
    AIRollbackAnalysis,
)
from agents.core.utilities.ai_client import AIClient


class TestAIRollbackAnalysis(unittest.TestCase):
    """Unit tests for the AIRollbackAnalysis class."""

    def setUp(self):
        """Sets up an instance of AIRollbackAnalysis for testing."""
        self.manager = AIRollbackAnalysis()
        self.error_signature = "example_error_signature"
        self.test_patch = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ fixed code"""

    def tearDown(self):
        """Cleanup after tests by removing any created test files."""
        for file in [
            FAILED_PATCHES_FILE,
            REFINED_PATCHES_FILE,
            HUMAN_REVIEW_FILE,
            AI_DECISIONS_LOG,
            PATCH_HISTORY_FILE,
        ]:
            if os.path.exists(file):
                os.remove(file)

    def test_track_patch_history(self):
        """Test logging of patch history."""
        self.manager.track_patch_history(self.error_signature, self.test_patch, "Failed")

        with open(PATCH_HISTORY_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

        self.assertIn(self.error_signature, logs)
        self.assertEqual(logs[self.error_signature][0]["status"], "Failed")

    @patch("agents.core.utilities.ai_client.AIClient.evaluate_patch_with_reason")
    def test_analyze_failed_patches(self, mock_evaluate_patch):
        """Test AI-based classification of failed patches."""
        mock_evaluate_patch.side_effect = lambda patch: {"score": 80, "reason": "Good structure"}
        self.manager.patch_tracker.get_failed_patches = MagicMock(return_value=[self.test_patch])

        refinable, bad, uncertain = self.manager.analyze_failed_patches(self.error_signature)

        self.assertIn(self.test_patch, refinable)
        self.assertEqual(bad, [])
        self.assertEqual(uncertain, [])

    @patch("agents.core.utilities.ai_client.AIClient.refine_patch", return_value="--- a/code.py\n+++ b/code.py\n@@ -1 +1 @@\n- old code\n+ refined code")
    @patch("agents.core.utilities.ai_rollback_analysis.AIRollbackAnalysis.analyze_failed_patches", return_value=(["test_patch"], [], []))
    def test_refine_patches_success(self, mock_analyze_patches, mock_refine_patch):
        """Test refinement of AI-correctable patches."""
        result = self.manager.refine_patches(self.error_signature)
        self.assertTrue(result)

    @patch("agents.core.utilities.ai_rollback_analysis.AIRollbackAnalysis.analyze_failed_patches", return_value=([], [], []))
    def test_refine_patches_no_refinable(self, mock_analyze_patches):
        """Test refinement process when no refinable patches exist."""
        result = self.manager.refine_patches(self.error_signature)
        self.assertFalse(result)

    @patch("agents.core.utilities.ai_rollback_analysis.AIRollbackAnalysis.refine_patches", return_value=True)
    def test_process_failed_patches_success(self, mock_refine_patches):
        """Test full failed patch processing when refinement succeeds."""
        result = self.manager.process_failed_patches(self.error_signature)
        self.assertTrue(result)

    @patch("agents.core.utilities.ai_rollback_analysis.AIRollbackAnalysis.refine_patches", return_value=False)
    def test_process_failed_patches_failure(self, mock_refine_patches):
        """Test full failed patch processing when no refinements are possible."""
        result = self.manager.process_failed_patches(self.error_signature)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()