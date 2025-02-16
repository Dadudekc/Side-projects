import json
import os
import unittest
from unittest.mock import MagicMock, patch

from agents.core.AgentBase import AgentBase
from agents.core.utilities.ai_patch_utils import AIPatchUtils
from agents.custom_agent import CustomAgent
from ai_engine.models.ai_model_manager import AIModelManager
from ai_engine.models.deepseek_model import DeepSeekModel
from ai_engine.models.mistral_model import MistralModel
from ai_engine.models.openai_model import OpenAIModel

AI_PERFORMANCE_TRACKER_FILE = "path/to/tracker/file.json"


class TestOpenAIModel(unittest.TestCase):
    """Unit tests for the OpenAIModel class."""

    def setUp(self):
        """Sets up an instance of OpenAIModel for testing."""
        self.model = OpenAIModel()
        self.error_message = "SyntaxError: unexpected EOF while parsing"
        self.code_context = "def test_function():\n    print('Hello, World!')\n"
        self.test_file = "test_script.py"

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
    def test_generate_patch(self, mock_openai):
        """Test patch generation with retries and validation."""
        mock_openai.side_effect = [
            None,
            "diff --git patch",
        ]  # First attempt fails, second succeeds
        patch_result = self.model.generate_patch(
            self.error_message, self.code_context, self.test_file
        )
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
        self.model._record_ai_performance("OpenAI", success=True)
        self.model._record_ai_performance("OpenAI", success=False)

        with open(AI_PERFORMANCE_TRACKER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["OpenAI"]["success"], 1)
        self.assertEqual(data["OpenAI"]["fail"], 1)


if __name__ == "__main__":
    unittest.main()
