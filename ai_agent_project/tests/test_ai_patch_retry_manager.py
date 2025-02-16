import unittest
from unittest.mock import MagicMock, patch

from agents.core.utilities.ai_patch_retry_manager import AIPatchRetryManager
from agents.core.utilities.ai_confidence_manager import AIConfidenceManager
from agents.core.utilities.ai_patch_analyzer import AIPatchAnalyzer
from agents.core.utilities.auto_fix_manager import AutoFixManager


class TestAIPatchRetryManager(unittest.TestCase):
    """Unit tests for the AIPatchRetryManager class."""

    def setUp(self):
        """Sets up an instance of AIPatchRetryManager for testing."""
        self.manager = AIPatchRetryManager()
        self.error_signature = "example_error_signature"
        self.failed_patch = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ fixed code"""
        self.failed_patches = {self.error_signature: [self.failed_patch]}

    @patch("agents.core.utilities.ai_patch_analyzer.AIPatchAnalyzer.analyze_failed_patch")
    @patch("agents.core.utilities.ai_confidence_manager.AIConfidenceManager.get_confidence")
    @patch("agents.core.utilities.ai_patch_analyzer.AIPatchAnalyzer.modify_failed_patch")
    @patch("agents.core.utilities.auto_fix_manager.AutoFixManager.debugging_strategy.apply_patch")
    def test_retry_failed_patches_success(self, mock_apply_patch, mock_modify_patch, mock_get_confidence, mock_analyze_failed_patch):
        """Test AI patch retry process when a patch modification is successful."""
        mock_analyze_failed_patch.return_value = ("Patch failed due to syntax error", 0.3)
        mock_get_confidence.return_value = 0.5  # Initial confidence
        mock_modify_patch.return_value = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ modified code"""
        mock_apply_patch.return_value = True  # Simulate successful patch application

        self.manager.retry_failed_patches(self.failed_patches)

        mock_analyze_failed_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_modify_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_apply_patch.assert_called_once()

    @patch("agents.core.utilities.ai_patch_analyzer.AIPatchAnalyzer.analyze_failed_patch")
    @patch("agents.core.utilities.ai_confidence_manager.AIConfidenceManager.get_confidence")
    @patch("agents.core.utilities.ai_patch_analyzer.AIPatchAnalyzer.modify_failed_patch")
    @patch("agents.core.utilities.auto_fix_manager.AutoFixManager.debugging_strategy.apply_patch")
    def test_retry_failed_patches_failure(self, mock_apply_patch, mock_modify_patch, mock_get_confidence, mock_analyze_failed_patch):
        """Test AI patch retry process when a patch modification fails."""
        mock_analyze_failed_patch.return_value = ("Patch failed due to syntax error", 0.2)
        mock_get_confidence.return_value = 0.5  # Initial confidence
        mock_modify_patch.return_value = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ modified code"""
        mock_apply_patch.return_value = False  # Simulate a failed patch application

        self.manager.retry_failed_patches(self.failed_patches)

        mock_analyze_failed_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_modify_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_apply_patch.assert_called_once()

    @patch("agents.core.utilities.ai_patch_analyzer.AIPatchAnalyzer.analyze_failed_patch")
    @patch("agents.core.utilities.ai_confidence_manager.AIConfidenceManager.get_confidence")
    def test_retry_failed_patches_low_confidence(self, mock_get_confidence, mock_analyze_failed_patch):
        """Test AI patch retry when confidence remains too low."""
        mock_analyze_failed_patch.return_value = ("Patch failed due to syntax error", 0.1)
        mock_get_confidence.return_value = 0.5  # Confidence remains below threshold

        self.manager.retry_failed_patches(self.failed_patches)

        mock_analyze_failed_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_get_confidence.assert_called_once_with(self.error_signature)


if __name__ == "__main__":
    unittest.main()