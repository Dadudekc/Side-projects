"""
This module contains unit tests for the DebugAgentUtils class.

It includes test cases for the following methods:
- deepseek_chunk_code: Ensures correct chunking of code into smaller pieces.
- run_deepseek_ollama_analysis: Tests a fallback system using Ollama and DeepSeek.
- parse_diff_suggestion: Ensures correct parsing of a patch.
- rollback_changes: Tests whether rollback_changes correctly restores files.
"""

import os
import unittest
from unittest.mock import MagicMock, patch
from unidiff import PatchSet
from io import StringIO

from agents.core.utilities.debug_agent_utils import DebugAgentUtils  # Ensure correct import


class TestDebugAgentUtils(unittest.TestCase):
    """Unit tests for the DebugAgentUtils class."""

    def setUp(self):
        """Set up test case variables."""
        self.sample_code = "def hello():\n    pass\n    print('Hello, World!')\n"
        self.error_msg = "SyntaxError: unexpected EOF while parsing"

    def test_deepseek_chunk_code(self):
        """Test deepseek_chunk_code to ensure correct chunking of code."""
        chunks = DebugAgentUtils.deepseek_chunk_code(self.sample_code, max_chars=10)

        # Ensure correct chunking behavior
        expected_chunks = [
            "def hello(",
            "):\n    pas",
            "s\n    prin",
            "t('Hello, ",
            "World!')\n"
        ]

        self.assertEqual(len(chunks), len(expected_chunks))
        self.assertEqual(chunks, expected_chunks)

    @patch("subprocess.run")
    def test_run_deepseek_ollama_analysis(self, mock_subprocess):
        """Test Ollama and DeepSeek fallback system."""
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="diff --git patch\n")

        chunks = DebugAgentUtils.deepseek_chunk_code(self.sample_code, max_chars=10)
        result = DebugAgentUtils.run_deepseek_ollama_analysis(chunks, self.error_msg)

        self.assertIn("diff --git", result)

    def test_parse_diff_suggestion(self):
        """Test parse_diff_suggestion to ensure it correctly parses a patch."""
        diff_text = """\
diff --git a/test.py b/test.py
index 83db48f..bf3d45c 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,3 @@
 def hello():
    pass
-    print('Hello, World!')
+    print('Hello, Universe!')
"""

        patch = DebugAgentUtils.parse_diff_suggestion(diff_text)

        # Ensure PatchSet is parsed correctly
        parsed_patch = PatchSet(StringIO(diff_text))  # Use StringIO to simulate a file-like object
        self.assertIsInstance(parsed_patch, PatchSet)
        self.assertGreater(len(parsed_patch), 0)  # Ensure patch has at least one change

    @patch("subprocess.run")
    def test_rollback_changes(self, mock_subprocess):
        """Test rollback_changes to ensure Git restore is called correctly."""
        DebugAgentUtils.rollback_changes(["test.py"])
        mock_subprocess.assert_called_with(["git", "restore", "test.py"], check=True)

    def test_queue_additional_agents(self):
        """Test queue_additional_agents to ensure agents are queued properly."""
        result = DebugAgentUtils.queue_additional_agents(["AgentA", "AgentB"])
        self.assertEqual(result["status"], "queued")
        self.assertIn("AgentA", result["agents"])
        self.assertIn("AgentB", result["agents"])


if __name__ == "__main__":
    unittest.main()
