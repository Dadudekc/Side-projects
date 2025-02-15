import unittest
from unittest.mock import patch, MagicMock
from agents.core.core import (
    AgentBase,
    AIModelManager,
    AIPatchUtils,
    CustomAgent,
    DeepSeekModel,
    MistralModel,
    OpenAIModel,
)


class TestAIPatchUtils(unittest.TestCase):

    def test_chunk_code(self):
        file_content = "a" * 2500  # Simulate a long file content
        chunks = AIPatchUtils.chunk_code(file_content, max_chars=1000)
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(len(chunk) <= 1000 for chunk in chunks))

    @patch("subprocess.run")
    def test_query_llm_success(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="Suggested patch")
        response = AIPatchUtils.query_llm("Test prompt", "mistral")
        self.assertEqual(response, "Suggested patch")

    @patch("subprocess.run")
    def test_query_llm_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="Error occurred")
        response = AIPatchUtils.query_llm("Test prompt", "mistral")
        self.assertIsNone(response)

    @patch("openai.ChatCompletion.create")
    def test_query_openai_success(self, mock_openai):
        mock_openai.return_value = {
            "choices": [{"message": {"content": "Patch suggestion"}}]
        }
        response = AIPatchUtils.query_openai("Test prompt")
        self.assertEqual(response, "Patch suggestion")

    @patch("openai.ChatCompletion.create", side_effect=Exception("API error"))
    def test_query_openai_failure(self, mock_openai):
        response = AIPatchUtils.query_openai("Test prompt")
        self.assertIsNone(response)

    @patch.object(AIPatchUtils, "query_llm", side_effect=[None, "DeepSeek Patch"])
    @patch.object(AIPatchUtils, "query_openai", return_value="OpenAI Patch")
    def test_generate_patch_fallback_to_deepseek(
        self, mock_query_openai, mock_query_llm
    ):
        file_content = "def test_function():\n    return 42"
        error_msg = "SyntaxError: invalid syntax"
        patch = AIPatchUtils.generate_patch(file_content, error_msg)
        self.assertEqual(patch, "DeepSeek Patch")

    @patch.object(AIPatchUtils, "query_llm", return_value=None)
    @patch.object(AIPatchUtils, "query_openai", return_value="OpenAI Patch")
    def test_generate_patch_fallback_to_openai(self, mock_query_openai, mock_query_llm):
        file_content = "def test_function():\n    return 42"
        error_msg = "SyntaxError: invalid syntax"
        patch = AIPatchUtils.generate_patch(file_content, error_msg)
        self.assertEqual(patch, "OpenAI Patch")

    @patch.object(AIPatchUtils, "query_llm", return_value=None)
    @patch.object(AIPatchUtils, "query_openai", return_value=None)
    def test_generate_patch_no_suggestions(self, mock_query_openai, mock_query_llm):
        file_content = "def test_function():\n    return 42"
        error_msg = "SyntaxError: invalid syntax"
        patch = AIPatchUtils.generate_patch(file_content, error_msg)
        self.assertEqual(patch, "")


if __name__ == "__main__":
    unittest.main()
