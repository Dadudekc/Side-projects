import unittest
import os
import json
from unittest.mock import patch, MagicMock
from agents.core.AIPatchReviewManager import AIPatchReviewManager import AIPatchReviewManager, HUMAN_REVIEW_FILE, PATCH_RANKINGS_FILE, DETAILED_ERROR_LOG_FILE

class TestAIPatchReviewManager(unittest.TestCase):
    """"
"""    Unit tests for the AIPatchReviewManager class. """"    """ """"""
"    def setUp(self):"
"        """ """"""        Sets up an instance of AIPatchReviewManager for testing.
"        """ """""        self.manager = AIPatchReviewManager()"
"        self.error_signature = "example_error_signature""
"        self.test_patch = "--- a/code.py\n+++ b/code.py\n@@ -1 +1 @@\n- old code\n+ fixed code""
    def tearDown(self):
        """ """"""        Cleanup after tests by removing any created test files. """"        """
""        for file in [HUMAN_REVIEW_FILE, PATCH_RANKINGS_FILE, DETAILED_ERROR_LOG_FILE]:
"            if os.path.exists(file):"
"                os.remove(file)"

    @patch("agents.core.AIPatchReviewManager.AIClient.evaluate_patch_with_reason")
    def test_rank_human_reviewed_patches(self, mock_evaluate_patch):
        """ """"""        Test AI ranking of human-reviewed patches. """"        """ """""        mock_evaluate_patch.side_effect = lambda patch: {"score": 0.8, "reason": "Good fix"}"""
"        self.manager.human_review = {"            self.error_signature: [self.test_patch, "--- a/code.py\n+++ b/code.py\n@@ -1 +1 @@\n- old code\n+ better fix"]
        }

        self.manager.rank_human_reviewed_patches()
        self.assertIn(self.error_signature, self.manager.patch_rankings)
        self.assertGreater(len(self.manager.patch_rankings[self.error_signature]), 0)

    def test_log_patch_attempt(self):
        """"
"""        Test logging of patch attempts. """"        """ """""        self.manager.log_patch_attempt(self.error_signature, self.test_patch, "Applied Successfully", "Fixed import issue")"
"""        with open(DETAILED_ERROR_LOG_FILE, "r", encoding="utf-8") as f:"
            logs = json.load(f)

        self.assertIn(self.error_signature, logs)
        self.assertEqual(logs[self.error_signature][0]["outcome"], "Applied Successfully")

    def test_get_best_patch(self):
        """ """"""        Test retrieving the highest-ranked patch."
"        """ """""        self.manager.patch_rankings = {self.error_signature: [self.test_patch]}"
"        best_patch = self.manager.get_best_patch(self.error_signature)"
"        self.assertEqual(best_patch, self.test_patch)"
    @patch("agents.core.AIPatchReviewManager.AIPatchReviewManager.rank_human_reviewed_patches")
    @patch("agents.core.AIPatchReviewManager.PatchTrackingManager.apply_patch", return_value=True)
    def test_process_human_reviewed_patches_success(self, mock_apply_patch, mock_rank_patches):
        """ """"""        Test processing of human-reviewed patches when application succeeds. """"        """
""        self.manager.patch_rankings = {self.error_signature: [self.test_patch]}
"        self.manager.process_human_reviewed_patches()"
""
        with open(DETAILED_ERROR_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

        self.assertIn(self.error_signature, logs)
        self.assertEqual(logs[self.error_signature][0]["outcome"], "Applied Successfully")

    @patch("agents.core.AIPatchReviewManager.AIPatchReviewManager.rank_human_reviewed_patches")
    @patch("agents.core.AIPatchReviewManager.PatchTrackingManager.apply_patch", return_value=False)
    def test_process_human_reviewed_patches_failure(self, mock_apply_patch, mock_rank_patches):
        """ """"""        Test processing of human-reviewed patches when application fails. """"        """ """""        self.manager.patch_rankings = {self.error_signature: [self.test_patch]}""        self.manager.process_human_reviewed_patches()"
""        with open(DETAILED_ERROR_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

        self.assertIn(self.error_signature, logs)
        self.assertEqual(logs[self.error_signature][0]["outcome"], "Failed to Apply")

    def test_analyze_patch_failures(self):
        """"
"""        Test analysis of common patch failure patterns. """"        """ """""        self.manager.detailed_logs = {"
"            self.error_signature: [""                {"patch": self.test_patch, "outcome": "Failed to Apply", "extra_info": "Syntax error"},"
                {"patch": self.test_patch, "outcome": "Failed to Apply", "extra_info": "Import missing"}
            ]
        }

        failure_patterns = self.manager.analyze_patch_failures()
        self.assertIn("Syntax error", failure_patterns[self.error_signature])
        self.assertIn("Import missing", failure_patterns[self.error_signature])

if __name__ == "__main__":
    unittest.main()
