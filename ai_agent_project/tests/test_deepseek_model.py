"""

This module is for testing the DeepSeekModel class. The DeepSeekModel class is a model class for interacting with AI debugging engine using DeepSeek AI. The following functionalities are tested in this module:

1. Test if the DeepSeek AI and OpenAI GPT-4 are able to accurately generate patch data.
2. Test if the formatting of debugging prompts is correct.
3. Test whether the prompt can be properly modified for AI retries.
4. Check if the patch validation happens accurately based
"""

import json
import os
import random
import unittest
from unittest.mock import MagicMock, patch

from ai_engine.models.deepseek_model import DeepSeekModel  # Adjust path if needed

AI_PERFORMANCE_TRACKER_FILE = "ai_performance.json"


class TestDeepSeekModel(unittest.TestCase):
    """Unit tests for the DeepSeekModel class."""

    def setUp(self):
        """Sets up an instance of DeepSeekModel for testing."""
        self.model = DeepSeekModel()
        self.error_message = "SyntaxError: unexpected EOF while parsing"
        self.code_context = "def test_function():\n    pass\n    print('Hello, World!')"
        self.test_file = "test_script.py"

        # Ensure AI performance tracking file exists before testing
        if not os.path.exists(AI_PERFORMANCE_TRACKER_FILE):
            with open(AI_PERFORMANCE_TRACKER_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def tearDown(self):
        """Cleanup after tests by removing AI performance tracking file if created."""
        if os.path.exists(AI_PERFORMANCE_TRACKER_FILE):
            os.remove(AI_PERFORMANCE_TRACKER_FILE)

    @patch("ai_engine.models.deepseek_model.subprocess.run")
    def test_generate_with_deepseek(self, mock_subprocess):
        """Test calling DeepSeek AI for patch generation."""
        mock_subprocess.return_value = MagicMock(
            returncode=0, stdout="diff --git patch"
        )

        patch_result = self.model._generate_with_deepseek("test_prompt")

        self.assertIn("diff --git", patch_result)

    @patch("ai_engine.models.deepseek_model.openai.ChatCompletion.create")
    def test_generate_with_openai(self, mock_openai):
        """Test OpenAI GPT-4 fallback."""
        mock_openai.return_value = {
            "choices": [{"message": {"content": "diff --git patch"}}]
        }

        patch_result = self.model._generate_with_openai("test_prompt")

        self.assertIn("diff --git", patch_result)

    def test_format_prompt(self):
        """Test formatting of debugging prompts."""
        prompt = self.model._format_prompt(
            self.error_message, self.code_context, self.test_file
        )

        self.assertIn("SyntaxError", prompt)
        self.assertIn("test_script.py", prompt)

    def test_modify_prompt(self):
        """Test modifying prompts for AI retries."""
        prompt = self.model._format_prompt(
            self.error_message, self.code_context, self.test_file
        )
        modified_prompt = self.model._modify_prompt(prompt, 1)

        self.assertIn("Avoid modifying unrelated lines of code.", modified_prompt)

    @patch.object(DeepSeekModel, "_generate_with_deepseek")
    @patch.object(DeepSeekModel, "_generate_with_openai")
    @patch("random.uniform", return_value=0.9)  # Ensures validation always passes
    def test_generate_patch(self, mock_random, mock_openai, mock_deepseek):
        """Test patch generation with fallback and validation."""
        # Simulating DeepSeek failing three times before success
        mock_deepseek.side_effect = [
            None,  # 1st attempt fails
            None,  # 2nd attempt fails
            None,  # 3rd attempt fails
            "diff --git patch",  # 4th attempt succeeds
        ]
        mock_openai.return_value = None  # OpenAI should only be used if DeepSeek fails

        patch_result = self.model.generate_patch(
            self.error_message, self.code_context, self.test_file
        )

        # Assert that a valid patch was returned
        self.assertIsNotNone(patch_result)
        self.assertIn("diff --git", patch_result)

    @patch("random.uniform", return_value=0.8)
    def test_validate_patch(self, mock_random):
        """Test patch validation with a high confidence score."""
        result = self.model._validate_patch("diff --git patch")

        self.assertTrue(result)

    @patch("random.uniform", return_value=0.6)
    def test_validate_patch_low_score(self, mock_random):
        """Test patch validation rejection due to low confidence score."""
        result = self.model._validate_patch("diff --git patch")

        self.assertFalse(result)

    def test_ai_performance_tracking(self):
        """Test AI performance tracking by recording success and failure."""
        self.model._record_ai_performance("DeepSeek", success=True)
        self.model._record_ai_performance("OpenAI", success=False)

        with open(AI_PERFORMANCE_TRACKER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["DeepSeek"]["success"], 1)
        self.assertEqual(data["OpenAI"]["fail"], 1)


if __name__ == "__main__":
    unittest.main()
