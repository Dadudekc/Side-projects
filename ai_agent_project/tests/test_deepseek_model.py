import unittest
from unittest.mock import patch, MagicMock
import os
import json
from agents.core.core import (
    AgentBase,
    AIModelManager,
    AIPatchUtils,
    CustomAgent,
    DeepSeekModel,
    MistralModel,
    OpenAIModel,
)


class TestDeepSeekModel(unittest.TestCase):
    """Unit tests for the DeepSeekModel class."""

    def setUp(self):
        """Initialize DeepSeekModel before each test."""
        self.model = DeepSeekModel(model_path="test_model_path")

    @patch("subprocess.run")
    def test_generate_with_deepseek_success(self, mock_subprocess):
        """Test successful patch generation using DeepSeek."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="Generated Patch")
        result = self.model._generate_with_deepseek("Test Prompt")
        self.assertEqual(result, "Generated Patch")

    @patch("subprocess.run")
    def test_generate_with_deepseek_failure(self, mock_subprocess):
        """Test DeepSeek failure handling."""
        mock_subprocess.return_value = MagicMock(returncode=1, stderr="Error")
        result = self.model._generate_with_deepseek("Test Prompt")
        self.assertIsNone(result)

    @patch("openai.ChatCompletion.create")
    def test_generate_with_openai_success(self, mock_openai):
        """Test successful patch generation using OpenAI."""
        mock_openai.return_value = {
            "choices": [{"message": {"content": "OpenAI Patch"}}]
        }
        result = self.model._generate_with_openai("Test Prompt")
        self.assertEqual(result, "OpenAI Patch")

    @patch("openai.ChatCompletion.create", side_effect=Exception("API Error"))
    def test_generate_with_openai_failure(self, mock_openai):
        """Test OpenAI failure handling."""
        result = self.model._generate_with_openai("Test Prompt")
        self.assertIsNone(result)

    def test_validate_patch_success(self):
        """Test patch validation success scenario."""
        with patch("random.uniform", return_value=0.8):
            result = self.model._validate_patch("Sample Patch")
            self.assertTrue(result)

    def test_validate_patch_failure(self):
        """Test patch validation failure scenario."""
        with patch("random.uniform", return_value=0.6):
            result = self.model._validate_patch("Sample Patch")
            self.assertFalse(result)

    def test_modify_prompt_variations(self):
        """Test modifications to prompts for retries."""
        base_prompt = "Base Prompt"
        modified_prompt_1 = self.model._modify_prompt(base_prompt, 0)
        modified_prompt_2 = self.model._modify_prompt(base_prompt, 1)
        modified_prompt_3 = self.model._modify_prompt(base_prompt, 2)
        self.assertNotEqual(modified_prompt_1, modified_prompt_2)
        self.assertNotEqual(modified_prompt_2, modified_prompt_3)

    def test_load_ai_performance_empty(self):
        """Test AI performance loading when no file exists."""
        if os.path.exists("ai_performance.json"):
            os.remove("ai_performance.json")
        result = self.model._load_ai_performance()
        self.assertEqual(result, {})

    def test_save_ai_performance(self):
        """Test saving AI performance tracking data."""
        test_data = {"DeepSeek": {"success": 3, "fail": 2}}
        self.model.ai_performance = test_data
        self.model._save_ai_performance()
        with open("ai_performance.json", "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, test_data)

    @patch.object(
        DeepSeekModel,
        "_generate_patch_with_fallback",
        return_value=("Patch Data", "DeepSeek"),
    )
    @patch.object(DeepSeekModel, "_validate_patch", return_value=True)
    def test_generate_patch_success(self, mock_validate, mock_generate):
        """Test full patch generation success."""
        result = self.model.generate_patch("Error", "Code", "test.py")
        self.assertEqual(result, "Patch Data")

    @patch.object(
        DeepSeekModel, "_generate_patch_with_fallback", return_value=(None, "None")
    )
    def test_generate_patch_failure(self, mock_generate):
        """Test failure when no valid patch is generated."""
        result = self.model.generate_patch("Error", "Code", "test.py")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
