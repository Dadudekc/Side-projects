"""
This module contains unit tests for the AIModelManager class.
It tests, among other things:

- Setting up an instance of AIModelManager for testing purposes
- Making calls to local Ollama model and OpenAI GPT-4 as a fallback
- The generation of patches with model priority and confidence tracking
- The correct formatting of debugging prompts
- The generation of error signatures.

Test cases include class setup, calls to different AI models, patch generation with model priority and confidence.
"""

import unittest
from unittest.mock import MagicMock, patch
import subprocess
import openai

from ai_engine.ai_model_manager import AIModelManager
from ai_engine.models.confidence_manager import AIConfidenceManager

class TestAIModelManager(unittest.TestCase):
    def setUp(self):
        self.model_manager = AIModelManager()

    @patch("ai_engine.ai_model_manager.open", create=True)
    def test_save_model(self, mock_open):
        mock_open.return_value.__enter__.return_value.write = MagicMock()
        self.model_manager.save_model("test_model")
        mock_open.assert_called_once()

    @patch("ai_engine.ai_model_manager.open", create=True)
    def test_load_model(self, mock_open):
        mock_open.return_value.__enter__.return_value.read.return_value = "{}"
        result = self.model_manager.load_model("test_model")
        self.assertEqual(result, {})

        patch_result = self.manager._generate_with_openai("test_prompt")
        self.assertIsNotNone(patch_result)
        self.assertIn("diff --git", patch_result)

    @patch.object(AIConfidenceManager, "get_best_high_confidence_patch")
    @patch.object(AIConfidenceManager, "assign_confidence_score")
    @patch.object(AIModelManager, "_generate_with_model")
    def test_generate_patch(self, mock_generate_with_model, mock_assign_confidence, mock_get_best_patch):
        """Test patch generation with model priority and confidence tracking."""

        # No pre-existing high-confidence patch
        mock_get_best_patch.return_value = None
        mock_assign_confidence.return_value = (0.8, "AI predicts success")  # Assigns high confidence

        # First model generates a successful patch
        mock_generate_with_model.side_effect = ["diff --git patch", None, None]

        patch_result = self.manager.generate_patch(self.error_msg, self.code_context, self.test_file)
        self.assertIsNotNone(patch_result)
        self.assertIn("diff --git", patch_result)

    def test_format_prompt(self):
        """Test formatting of debugging prompts."""
        prompt = self.manager._format_prompt(self.error_msg, self.code_context, self.test_file)
        self.assertIn("SyntaxError", prompt)
        self.assertIn("test_script.py", prompt)

    def test_compute_error_signature(self):
        """Test error signature generation."""
        signature1 = self.manager._compute_error_signature(self.error_msg, self.code_context)
        signature2 = self.manager._compute_error_signature(self.error_msg, self.code_context)
        self.assertEqual(signature1, signature2)  # Should be deterministic


if __name__ == "__main__":
    unittest.main()
