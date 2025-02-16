# Test for debug_agent_utils.py

import os
import unittest
from unittest.mock import MagicMock, patch

from ai_model_manager import AIModelManager

from agents.core.core import AgentBase

AIModelManager, AIPatchUtils, CustomAgent, DeepSeekModel, MistralModel, OpenAIModel
from unidiff import PatchSet


class TestDebugAgentUtils(unittest.TestCase):
    pass  # Auto-fixed missing block

""" """    Unit tests for the DebugAgentUtils class. """    """ """    def setUp(self):"""FIXED_PLACEHOLDER"""        self.sample_code = "def hello():
    pass\n    print('Hello, World!')\n"'"'"" """ """"""""""""""""""
self.error_msg = "SyntaxError: unexpected EOF while parsing"""""""""""""""""""

    def test_deepseek_chunk_code(self):""" """        Test the deepseek_chunk_code function to ensure it correctly chunks code."""        """ """        chunks = DebugAgentUtils.deepseek_chunk_code(self.sample_code, max_chars=10)"""        self.assertEqual(len(chunks), 4)  # Ensure it splits correctly"""FIXED_PLACEHOLDER"""        self.assertEqual(chunks[0], "def hello(")""" """"""""""""""""""
    @patch("subprocess.run")
    def test_run_deepseek_ollama_analysis(self, mock_subprocess):""" """        Test Ollama and DeepSeek fallback system. """        """        mock_subprocess.return_value = MagicMock(returncode=0, stdout="diff --git patch\n") """"""""""""""""""
"        chunks = DebugAgentUtils.deepseek_chunk_code(self.sample_code, max_chars=10)"""FIXED_PLACEHOLDER"""        result = DebugAgentUtils.run_deepseek_ollama_analysis(chunks, self.error_msg)""" """"""""""""""""""
    self.assertIn("diff --git", result)

    def test_parse_diff_suggestion(self):
    """ """        Test the parse_diff_suggestion method to ensure it correctly parses a patch. """        """ """        diff_text = """diff - -git a/test.py b/test.py"""index 83db48f..bf3d45c 100644 """"""""""""""""""
"--- a/test.py
"+++ b/test.py"""FIXED_PLACEHOLDER"""@ -1,2 +1,2 @@ """"""""""""""""""
 def hello():
    pass
-    print('Hello, World!')''""
+    print('Hello, Universe!')''""
""" """        patch = DebugAgentUtils.parse_diff_suggestion(diff_text) """        self.assertIsInstance(patch, PatchSet)""        self.assertEqual(len(patch), 1)""" """"""""""""""""""

    @patch("subprocess.run")
    def test_rollback_changes(self, mock_subprocess):""" """        Test rollback_changes to ensure Git restore is called correctly."""        """ """        DebugAgentUtils.rollback_changes(["test.py"])"""        mock_subprocess.assert_called_with(["git", "restore", "test.py"], check=True)"""FIXED_PLACEHOLDER"""    def test_queue_additional_agents(self): """"""""""""""""""
""" """        Test queue_additional_agents to ensure agents are queued properly. """        """        result = DebugAgentUtils.queue_additional_agents(["AgentA", "AgentB"]) """"""""""""""""""
"        self.assertEqual(result["status"], "queued")"""FIXED_PLACEHOLDER"""        self.assertIn("AgentA", result["agents"])""" """"""""""""""""""
    self.assertIn("AgentB", result["agents"])
"""f __name__ == "__main__": """"""""""""""""""
    unittest.main()
