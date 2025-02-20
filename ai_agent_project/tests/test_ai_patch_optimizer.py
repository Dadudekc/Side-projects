import unittest
from unittest.mock import patch
from ai_engine.patch_optimizer import AIPatchOptimizer
from agents.core.utilities.ai_model_manager import AIModelManager
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager
from ai_engine.confidence_manager import AIConfidenceManager

class TestAIPatchOptimizer(unittest.TestCase):
    """Unit tests for the AIPatchOptimizer class."""

    def setUp(self):
        """Set up an instance of AIPatchOptimizer for testing."""
        self.optimizer = AIPatchOptimizer()
        self.error_signature = "example_error_signature"
        self.original_patch = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ fixed code"""

    @patch("ai_engine.models.debugger.patch_tracking_manager.PatchTrackingManager.get_failed_patches", return_value=[])
    @patch("ai_engine.confidence_manager.AIConfidenceManager.assign_confidence_score", return_value=(0.8, "Improved fix"))
    @patch("ai_engine.confidence_manager.AIConfidenceManager.get_confidence", return_value=0.6)
    def test_refine_failed_patch_success(self, mock_get_confidence, mock_assign_confidence, mock_get_failed_patches):
        """Test refining a failed patch when AI confidence improves."""
        modified_patch = self.optimizer.refine_failed_patch(self.error_signature, self.original_patch)
        self.assertIsNotNone(modified_patch)
        self.assertNotEqual(modified_patch, self.original_patch)

    @patch("ai_engine.models.debugger.patch_tracking_manager.PatchTrackingManager.get_failed_patches", return_value=["patch1", "patch2", "patch3"])
    def test_refine_failed_patch_max_attempts(self, mock_get_failed_patches):
        """Test that refining a patch fails after reaching max modification attempts."""
        modified_patch = self.optimizer.refine_failed_patch(self.error_signature, self.original_patch)
        self.assertIsNone(modified_patch)

    @patch("ai_engine.models.debugger.patch_tracking_manager.PatchTrackingManager.get_failed_patches", return_value=[])
    @patch("ai_engine.confidence_manager.AIConfidenceManager.assign_confidence_score", return_value=(0.5, "No improvement"))
    @patch("ai_engine.confidence_manager.AIConfidenceManager.get_confidence", return_value=0.6)
    def test_refine_failed_patch_low_confidence(self, mock_get_confidence, mock_assign_confidence, mock_get_failed_patches):
        """Test refining a failed patch when AI confidence does not improve."""
        modified_patch = self.optimizer.refine_failed_patch(self.error_signature, self.original_patch)
        self.assertIsNone(modified_patch)

    @patch("ai_engine.patch_optimizer.AIPatchOptimizer.refine_failed_patch",
           return_value="diff --git a/code.py\n+++ b/code.py\n@@ -1 +1 @@\n- old code\n+ modified code")
    @patch("agents.core.utilities.ai_model_manager.AIModelManager._generate_with_model", return_value="diff --git patch")
    def test_attempt_patch_reapply_success(self, mock_generate_with_model, mock_refine_failed_patch):
        """Test that a modified patch is successfully reapplied."""
        result = self.optimizer.attempt_patch_reapply(self.error_signature, "test_file.py", self.original_patch)
        self.assertTrue(result)

    @patch("ai_engine.patch_optimizer.AIPatchOptimizer.refine_failed_patch", return_value=None)
    def test_attempt_patch_reapply_failure(self, mock_refine_failed_patch):
        """Test that a patch reapply fails when no valid modifications are found."""
        result = self.optimizer.attempt_patch_reapply(self.error_signature, "test_file.py", self.original_patch)
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
