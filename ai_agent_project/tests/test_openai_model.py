"""
This module contains the unit test cases for the OpenAIModel class in the 'ai_engine.models.openai_model' module.

During the setup for the test cases, it ensures the existence of the AI performance tracking file and prepares an instance 
of the OpenAIModel for testing. If the tracking file doesn't exist, it would create it and log an empty dictionary. If it 
exists but either empty or corrupt, it would reset it. The AI performance tracking file is cleaned up or removed.
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch
import openai

from agents.core.AgentBase import AgentBase
from agents.core.utilities.ai_patch_utils import AIPatchUtils
from agents.custom_agent import CustomAgent
from ai_engine.models.ai_model_manager import AIModelManager  # Corrected import
from ai_engine.models.deepseek_model import DeepSeekModel
from ai_engine.models.mistral_model import MistralModel
from ai_engine.models.openai_model import OpenAIModel

AI_PERFORMANCE_TRACKER_FILE = "tracking_data/ai_performance.json"


class TestOpenAIModel(unittest.TestCase):
    """Unit tests for the OpenAIModel class."""

    def setUp(self):
        """Sets up an instance of OpenAIModel for testing."""
        self.model = OpenAIModel()
        self.error_message = "SyntaxError: unexpected EOF while parsing"
        self.code_context = "def test_function():\n    print('Hello, World!')\n"
        self.test_file = "test_script.py"

        # Ensure AI performance tracking file exists before testing
        if not os.path.exists(AI_PERFORMANCE_TRACKER_FILE):
            with open(AI_PERFORMANCE_TRACKER_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)  # Ensure an empty dictionary is written
        else:
            # If file exists but is empty or corrupt, reset it
            try:
                with open(AI_PERFORMANCE_TRACKER_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, dict):  # Ensure it's a valid dictionary
                    raise ValueError
            except (json.JSONDecodeError, ValueError):
                with open(AI_PERFORMANCE_TRACKER_FILE, "w", encoding="utf-8") as f:
                    json.dump({}, f)

    def tearDown(self):
        """Cleanup after tests by removing AI performance tracking file if created."""
        if os.path.exists(AI_PERFORMANCE_TRACKER_FILE):
            os.remove(AI_PERFORMANCE_TRACKER_FILE)

    @patch("ai_engine.models.openai_model.openai.ChatCompletion.create")
    def test_generate_with_openai(self, mock_openai):
        """Test calling OpenAI GPT-4 Turbo for patch generation."""
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

    @patch.object(OpenAIModel, "_generate_with_openai")
    @patch("random.uniform", return_value=0.9)  # Mock confidence to always be high enough
    def test_generate_patch(self, mock_random, mock_openai):
        """Test patch generation with retries and validation."""
        mock_openai.side_effect = [
            None,  # First attempt fails
            "diff --git patch",  # Second attempt succeeds
        ]

        patch_result = self.model.generate_patch(
            self.error_message, self.code_context, self.test_file
        )

        if not patch_result:
            self.fail("❌ Patch generation returned an empty result unexpectedly.")

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
        self.model._record_ai_performance("OpenAIModel", success=True)
        self.model._record_ai_performance("OpenAIModel", success=False)

        with open(AI_PERFORMANCE_TRACKER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["OpenAIModel"]["success"], 1)
        self.assertEqual(data["OpenAIModel"]["fail"], 1)

    @patch("ai_engine.models.openai_model.openai.ChatCompletion.create")
    def test_generate_with_openai_fails_without_api_key(self, mock_openai):
        """Ensure that OpenAI GPT-4 does not attempt to generate patches if the API key is missing."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):  # Simulate missing API key
            mock_openai.return_value = None  # Explicitly return None for clarity
            patch_result = self.model._generate_with_openai("test_prompt")
            self.assertIsNone(patch_result, "OpenAI generation should return None if API key is missing.")

    @patch("ai_engine.models.openai_model.openai.ChatCompletion.create")
    def test_generate_with_openai_exception_handling(self, mock_openai):
        """Ensure OpenAI API failures are handled gracefully."""
        # Correctly setting up the side effect within the test method
        mock_openai.side_effect = openai.OpenAIError("API Error")

        # Attempt to generate using the OpenAI model
        patch_result = self.model._generate_with_openai("test_prompt")

        # Assert that the result is None due to the simulated API error
        self.assertIsNone(patch_result)
        # Additional logging assertions can be added here if needed

if __name__ == "__main__":
    unittest.main()
