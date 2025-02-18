import unittest
from unittest.mock import MagicMock, patch

from agents.core.utilities.AgentBase import AIModelManager  # Fixed import


class TestAIModelManager(unittest.TestCase):
    """Unit tests for the AIModelManager class."""

    def setUp(self):
        """Set up an instance of AIModelManager for testing."""
        self.manager = AIModelManager()
        self.error_msg = "SyntaxError: unexpected EOF while parsing"
        self.code_context = """def test_function():
    pass
    print('Hello, World!')"""
        self.test_file = "test_script.py"

    @patch("agents.core.utilities.AgentBase.AIModelManager.subprocess.run")
    def test_generate_with_ollama(self, mock_subprocess):
        """Test calling a local Ollama model."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="diff --git patch")
        
        patch_result = self.manager._generate_with_ollama("mistral", "test_prompt")
        self.assertIsNotNone(patch_result)
        self.assertIn("diff --git", patch_result)

    @patch("agents.core.utilities.AgentBase.AIModelManager.openai.ChatCompletion.create")
    def test_generate_with_openai(self, mock_openai):
        """Test OpenAI GPT-4 fallback."""
        mock_openai.return_value = {
            "choices": [{"message": {"content": "diff --git patch"}}]
        }

        patch_result = self.manager._generate_with_openai("test_prompt")
        self.assertIsNotNone(patch_result)
        self.assertIn("diff --git", patch_result)

    @patch.object(AIModelManager, "_generate_with_model")
    @patch.object(AIModelManager, "_compute_error_signature")
    @patch.object(AIModelManager, "confidence_manager")
    def test_generate_patch(self, mock_confidence_manager, mock_compute_signature, mock_generate_with_model):
        """Test patch generation with model priority and confidence tracking."""
        mock_compute_signature.return_value = "test_signature"
        mock_confidence_manager.get_confidence.return_value = 0.5
        mock_confidence_manager.assign_confidence_score.return_value = (0.8, "Improved confidence")

        # First model succeeds
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
