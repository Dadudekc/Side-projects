import unittest
from unittest.mock import patch
from ai_engine.models.debugger.ai_patch_retry_manager import AIPatchRetryManager
from ai_engine.confidence_manager import AIConfidenceManager
from ai_engine.models.debugger.auto_fix_manager import AutoFixManager
from ai_engine.patch_analyzer import AIPatchAnalyzer

class TestAIPatchRetryManager(unittest.TestCase):
    """Unit tests for the AIPatchRetryManager class."""

    def setUp(self):
        """Sets up an instance of AIPatchRetryManager for testing."""
        self.confidence_manager = AIConfidenceManager()
        self.auto_fix_manager = AutoFixManager()
        self.patch_analyzer = AIPatchAnalyzer()
        self.manager = AIPatchRetryManager(
            confidence_manager=self.confidence_manager,
            auto_fix_manager=self.auto_fix_manager,
            patch_analyzer=self.patch_analyzer,
        )
        self.error_signature = "example_error_signature"
        self.failed_patch = """--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ fixed code"""
        self.failed_patches = {self.error_signature: [self.failed_patch]}

    @patch.object(AIPatchAnalyzer, "analyze_failed_patch", return_value=("Patch failed due to syntax error", 0.3))
    @patch.object(AIPatchAnalyzer, "modify_failed_patch", return_value="""--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ modified code""")
    @patch.object(AIConfidenceManager, "calculate_confidence", return_value=0.5)
    @patch.object(AutoFixManager, "apply_patch", return_value=True)
    def test_retry_failed_patches_success(self, mock_apply_patch, mock_get_confidence, mock_modify_patch, mock_analyze_failed_patch):
        """Test AI patch retry process when a patch modification is successful."""
        self.manager.retry_failed_patches(self.failed_patches)

        mock_analyze_failed_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_modify_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_get_confidence.assert_called_once_with(self.error_signature)
        mock_apply_patch.assert_called_once()

    @patch.object(AIPatchAnalyzer, "analyze_failed_patch", return_value=("Patch failed due to syntax error", 0.2))
    @patch.object(AIPatchAnalyzer, "modify_failed_patch", return_value="""--- a/code.py
+++ b/code.py
@@ -1 +1 @@
- old code
+ modified code""")
    @patch.object(AIConfidenceManager, "calculate_confidence", return_value=0.5)
    @patch.object(AutoFixManager, "apply_patch", return_value=False)
    def test_retry_failed_patches_failure(self, mock_apply_patch, mock_get_confidence, mock_modify_patch, mock_analyze_failed_patch):
        """Test AI patch retry process when a patch modification fails."""
        self.manager.retry_failed_patches(self.failed_patches)

        mock_analyze_failed_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_modify_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_get_confidence.assert_called_once_with(self.error_signature)
        mock_apply_patch.assert_called_once()

    @patch.object(AIPatchAnalyzer, "analyze_failed_patch", return_value=("Patch failed due to syntax error", 0.1))
    @patch.object(AIConfidenceManager, "calculate_confidence", return_value=0.05)
    def test_retry_failed_patches_low_confidence(self, mock_get_confidence, mock_analyze_failed_patch):
        """Test AI patch retry when confidence remains too low."""
        # In this scenario, new confidence (0.05 + 0.1 = 0.15) is below the threshold 0.2.
        self.manager.retry_failed_patches(self.failed_patches)

        mock_analyze_failed_patch.assert_called_once_with(self.error_signature, self.failed_patch)
        mock_get_confidence.assert_called_once_with(self.error_signature)

        # Ensure that no modification or patch application occurs.
        with patch.object(AIPatchAnalyzer, "modify_failed_patch") as mock_modify, \
             patch.object(AutoFixManager, "apply_patch") as mock_apply:
            self.manager.retry_failed_patches(self.failed_patches)
            mock_modify.assert_not_called()
            mock_apply.assert_not_called()

if __name__ == "__main__":
    unittest.main()
