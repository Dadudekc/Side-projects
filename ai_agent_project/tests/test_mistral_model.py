"""

This module provides unit tests for the MistralModel class. This includes tests for defining
prompt formatting, using Mistral AI and OpenAI GPT-4 for patches generation, validation of patches
based on a confidence score, and performance tracking of AI models.

Methods are as follows:
- setUp: Sets up an instance of the MistralModel for testing and ensures that the AI performance tracking file exists.
- tearDown: Cleans up after tests by removing AI performance tracking file if created.
-
"""

import json
import os
import random
import unittest
from unittest.mock import MagicMock, patch

from ai_engine.models.mistral_model import MistralModel  # Ensure correct import path

# Define the correct AI performance tracking file
TRACKER_DIR = "tracking_data"
AI_PERFORMANCE_TRACKER_FILE = os.path.join(TRACKER_DIR, "ai_performance.json")


class TestMistralModel(unittest.TestCase):
    """Unit tests for the MistralModel class."""

    def setUp(self):
        """Sets up an instance of MistralModel for testing."""
        self.model = MistralModel()
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

    @patch("subprocess.run")
    def test_generate_with_mistral(self, mock_subprocess):
        """Test calling Mistral AI for patch generation."""
        mock_subprocess.return_value = MagicMock(
            returncode=0, stdout="diff --git patch"
        )

        patch_result = self.model._generate_with_mistral("test_prompt")

        self.assertIn("diff --git", patch_result)

    @patch("openai.ChatCompletion.create")
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

    @patch.object(MistralModel, "_generate_with_mistral")
    @patch.object(MistralModel, "_generate_with_openai")
    @patch("random.uniform", return_value=0.9)  # Mock confidence to always be high enough
    def test_generate_patch(self, mock_random, mock_openai, mock_mistral):
        """Test patch generation with fallback and validation."""
        # Ensure enough retries to match self.MAX_RETRIES
        mock_mistral.side_effect = [
            None,  # 1st attempt fails
            None,  # 2nd attempt fails
            None,  # 3rd attempt fails
            "diff --git patch",  # 4th attempt succeeds
        ]
        mock_openai.return_value = None  # OpenAI should only be used if Mistral fails

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
        self.model._record_ai_performance("Mistral", success=True)
        self.model._record_ai_performance("OpenAI", success=False)

        with open(AI_PERFORMANCE_TRACKER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["Mistral"]["success"], 1)
        self.assertEqual(data["OpenAI"]["fail"], 1)


if __name__ == "__main__":
    unittest.main()
