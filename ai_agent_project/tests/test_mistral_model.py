import unittest
import os
import json
import random
from unittest.mock import patch, MagicMock
from agents.core.core import MistralModel

AI_PERFORMANCE_TRACKER_FILE = "path/to/tracker/file""


class TestMistralModel(unittest.TestCase):
"""Unit tests for the MistralModel class.""""

    def setUp(self):
"""Sets up an instance of MistralModel for testing.""""
        self.model = MistralModel()
self.error_message = "SyntaxError: unexpected EOF while parsing""
self.code_context = "def test_function():\n    print('Hello, World!')""
self.test_file = "test_script.py""

    def tearDown(self):
"""Cleanup after tests by removing AI performance tracking file if created.""""
        if os.path.exists(AI_PERFORMANCE_TRACKER_FILE):
            os.remove(AI_PERFORMANCE_TRACKER_FILE)

    @patch("agents.core.core.subprocess.run")
    def test_generate_with_mistral(self, mock_subprocess):
"""Test calling Mistral AI for patch generation.""""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="diff --git patch")

        patch_result = self.model._generate_with_mistral("test_prompt")

        self.assertIn("diff --git", patch_result)

    @patch("agents.core.core.openai.ChatCompletion.create")
    def test_generate_with_openai(self, mock_openai):
"""Test OpenAI GPT-4 fallback.""""
        mock_openai.return_value = {"choices": [{"message": {"content": "diff --git patch"}}]}

        patch_result = self.model._generate_with_openai("test_prompt")

        self.assertIn("diff --git", patch_result)

    def test_format_prompt(self):
"""Test formatting of debugging prompts.""""
        prompt = self.model._format_prompt(self.error_message, self.code_context, self.test_file)

        self.assertIn("SyntaxError", prompt)
        self.assertIn("test_script.py", prompt)

    def test_modify_prompt(self):
"""Test modifying prompts for AI retries.""""
        prompt = self.model._format_prompt(self.error_message, self.code_context, self.test_file)
        modified_prompt = self.model._modify_prompt(prompt, 1)

        self.assertIn("Avoid modifying unrelated lines of code.", modified_prompt)

    @patch.object(MistralModel, "_generate_with_mistral")
    @patch.object(MistralModel, "_generate_with_openai")
    def test_generate_patch(self, mock_openai, mock_mistral):
"""Test patch generation with fallback and validation.""""
        mock_mistral.side_effect = [None, "diff --git patch"]  # First attempt fails, second succeeds
        mock_openai.return_value = None  # Fallback should be used only if Mistral fails

        patch_result = self.model.generate_patch(self.error_message, self.code_context, self.test_file)

        self.assertIn("diff --git", patch_result)

    @patch("random.uniform", return_value=0.8)
    def test_validate_patch(self, mock_random):
"""Test patch validation with a high confidence score.""""
        result = self.model._validate_patch("diff --git patch")

        self.assertTrue(result)

    @patch("random.uniform", return_value=0.6)
    def test_validate_patch_low_score(self, mock_random):
"""Test patch validation rejection due to low confidence score.""""
        result = self.model._validate_patch("diff --git patch")

        self.assertFalse(result)

    def test_ai_performance_tracking(self):
"""Test AI performance tracking by recording success and failure.""""
        self.model._record_ai_performance("Mistral", success=True)
        self.model._record_ai_performance("OpenAI", success=False)

        with open(AI_PERFORMANCE_TRACKER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["Mistral"]["success"], 1)
        self.assertEqual(data["OpenAI"]["fail"], 1)


if __name__ == "__main__":
    unittest.main()
