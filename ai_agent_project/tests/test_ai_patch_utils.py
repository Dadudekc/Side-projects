import unittest
from unittest.mock import MagicMock, patch
import logging
from openai import OpenAIError

from agents.core.utilities.ai_patch_utils import AIPatchUtils

# Set up logging for debugging
logger = logging.getLogger("TestAIPatchUtils")
logger.setLevel(logging.DEBUG)


class TestAIPatchUtils(unittest.TestCase):
    """Unit tests for AIPatchUtils."""

    def test_chunk_code(self):
        """Test that code chunking correctly splits long content."""
        file_content = "a" * 2500  # Simulate a long file content
        chunks = AIPatchUtils.chunk_code(file_content, max_chars=1000)
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(len(chunk) <= 1000 for chunk in chunks))

    @patch("subprocess.run")
    def test_query_llm_success(self, mock_run):
        """Test LLM query succeeds and returns a patch suggestion."""
        mock_run.return_value = MagicMock(returncode=0, stdout="diff --git\npatch content")
        response = AIPatchUtils.query_llm("Test prompt", "mistral")
        self.assertEqual(response, "diff --git\npatch content")

    @patch("subprocess.run")
    def test_query_llm_failure(self, mock_run):
        """Test LLM query fails and returns None."""
        mock_run.return_value = MagicMock(returncode=1, stderr="Error occurred")
        response = AIPatchUtils.query_llm("Test prompt", "mistral")
        self.assertIsNone(response)

    @patch("openai.ChatCompletion.create")
    def test_query_openai_success(self, mock_openai):
        """Test OpenAI query succeeds and returns a patch suggestion."""
        mock_openai.return_value = {
            "choices": [{"message": {"content": "diff --git\nPatch suggestion"}}]
        }
        response = AIPatchUtils.query_openai("Test prompt")
        self.assertEqual(response, "diff --git\nPatch suggestion")

    @patch("openai.ChatCompletion.create", side_effect=OpenAIError("API error"))
    def test_query_openai_failure(self, mock_openai):
        """Test OpenAI query failure returns None."""
        response = AIPatchUtils.query_openai("Test prompt")
        self.assertIsNone(response)

    @patch.object(AIPatchUtils, "query_llm", side_effect=[None, "diff --git\nDeepSeek Patch"])
    @patch.object(AIPatchUtils, "query_openai", return_value="diff --git\nOpenAI Patch")
    def test_generate_patch_fallback_to_deepseek(self, mock_query_openai, mock_query_llm):
        """Test that patch generation falls back to DeepSeek if Ollama fails."""
        file_content = """def test_function():
    pass
    return 42"""
        error_msg = "SyntaxError: invalid syntax"
        patch = AIPatchUtils.generate_patch(file_content, error_msg)

        logger.debug(f"Expected: 'DeepSeek Patch', Got: {patch}")
        self.assertEqual(patch, "diff --git\nDeepSeek Patch")

    @patch.object(AIPatchUtils, "query_llm", return_value=None)
    @patch.object(AIPatchUtils, "query_openai", return_value="diff --git\nOpenAI Patch")
    def test_generate_patch_fallback_to_openai(self, mock_query_openai, mock_query_llm):
        """Test that patch generation falls back to OpenAI if LLM fails."""
        file_content = """def test_function():
    pass
    return 42"""
        error_msg = "SyntaxError: invalid syntax"
        patch = AIPatchUtils.generate_patch(file_content, error_msg)

        logger.debug(f"Expected: 'OpenAI Patch', Got: {patch}")
        self.assertEqual(patch, "diff --git\nOpenAI Patch")

    @patch.object(AIPatchUtils, "query_llm", return_value=None)
    @patch.object(AIPatchUtils, "query_openai", return_value=None)
    def test_generate_patch_no_suggestions(self, mock_query_openai, mock_query_llm):
        """Test that patch generation returns an empty string if no AI suggests a fix."""
        file_content = """def test_function():
    pass
    return 42"""
        error_msg = "SyntaxError: invalid syntax"
        patch = AIPatchUtils.generate_patch(file_content, error_msg)

        logger.debug(f"Expected: '', Got: {patch}")
        self.assertEqual(patch, "")


if __name__ == "__main__":
    unittest.main()
