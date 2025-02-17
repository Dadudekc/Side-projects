import os
import shutil
import unittest
from unittest.mock import MagicMock, patch

from ai_engine.models.debugger.learning_db import LearningDB
from ai_engine.models.debugger.auto_fixer import AutoFixer
from agents.core.utilities.debug_agent_utils import DebugAgentUtils

class TestAutoFixer(unittest.TestCase):
    """Unit tests for the AutoFixer class."""

    def setUp(self):
        """Sets up an instance of AutoFixer for testing."""
        self.fixer = AutoFixer()
        self.failure = {
            "file": "tests/test_sample.py",
            "test": "test_function",
            "error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'",
        }
        self.test_files = {
            "tests/test_sample.py": "class TestClass:\n    def existing_method(self):\n        pass\n",
            "tests/test_assert.py": "assert 3 == 5\n",
            "tests/test_import.py": "# Some code without numpy\n",
            "tests/test_type.py": "example_function()\n",
            "tests/test_indent.py": "\tdef example_function():\n    pass\n\t\treturn 42\n"
        }
        
        os.makedirs("tests", exist_ok=True)

        for file, content in self.test_files.items():
            self._backup_and_create_file(file, content)

    def tearDown(self):
        """Cleanup only files created during testing, preventing full test deletion."""
        for file in self.test_files.keys():
            if os.path.exists(file):
                os.remove(file)
            backup_file = file + ".bak"
            if os.path.exists(backup_file):
                os.rename(backup_file, file)  # Restore original content

    def _backup_and_create_file(self, file_path, content):
        """Backs up an existing file and creates a new test file."""
        if os.path.exists(file_path):
            shutil.copy(file_path, file_path + ".bak")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    @patch("agents.core.utilities.auto_fixer.AutoFixer._apply_known_pattern", return_value=True)
    @patch("agents.core.utilities.learning_db.LearningDB.search_learned_fix", return_value=None)
    def test_apply_fix_with_known_pattern(self, mock_search_learned_fix, mock_apply_known_pattern):
        """Test fixing a known error pattern."""
        result = self.fixer.apply_fix(self.failure)
        self.assertTrue(result)

    @patch("agents.core.utilities.learning_db.LearningDB.search_learned_fix", return_value="def missing_attr(self):\n    pass")
    def test_apply_fix_with_learned_fix(self, mock_learned_fix):
        """Test applying a learned fix from the learning database."""
        result = self.fixer._apply_learned_fix(self.failure, "def missing_attr(self):\n    pass")
        self.assertTrue(result)
        with open(self.failure["file"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("def missing_attr(self):", content)

    @patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.apply_diff_patch", return_value=None)
    @patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.parse_diff_suggestion", return_value=[{"path": "tests/test_sample.py"}])
    @patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.run_deepseek_ollama_analysis", return_value="diff --git\n+ def missing_attr(self):\n    pass")
    def test_apply_fix_with_llm_patch(self, mock_apply_patch, mock_parse_diff, mock_run_llm):
        """Test applying an LLM-generated patch."""
        result = self.fixer._apply_llm_fix(self.failure)
        self.assertTrue(result)

    def test_quick_fix_missing_attribute(self):
        """Test auto-fixing a missing attribute in a class."""
        result = self.fixer._quick_fix_missing_attribute(self.failure["file"], self.failure["error"])
        self.assertTrue(result)
        with open(self.failure["file"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("def missing_attr(self):", content)

    def test_quick_fix_assertion_mismatch(self):
        """Test auto-fixing an assertion mismatch."""
        assertion_failure = {
            "file": "tests/test_assert.py",
            "error": "AssertionError: 3 != 5",
        }

        result = self.fixer._quick_fix_assertion_mismatch(assertion_failure["file"], assertion_failure["error"])
        self.assertTrue(result)

        with open(assertion_failure["file"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("assert 5 == 5", content)

    def test_quick_fix_import_error(self):
        """Test auto-fixing a missing import statement."""
        import_failure = {
            "file": "tests/test_import.py",
            "error": "ImportError: No module named 'numpy'",
        }

        result = self.fixer._quick_fix_import_error(import_failure["file"], import_failure["error"])
        self.assertTrue(result)

        with open(import_failure["file"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("import numpy", content)

    def test_quick_fix_type_error(self):
        """Test auto-fixing a function call with missing arguments."""
        type_error_failure = {
            "file": "tests/test_type.py",
            "error": "TypeError: example_function() missing 2 required positional arguments",
        }

        result = self.fixer._quick_fix_type_error(type_error_failure["file"], type_error_failure["error"])
        self.assertTrue(result)

        with open(type_error_failure["file"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("example_function(None, None)", content)

    def test_quick_fix_indentation(self):
        """Test auto-fixing an indentation error by converting tabs to spaces."""
        indentation_failure = {
            "file": "tests/test_indent.py",
            "error": "IndentationError: unexpected indent",
        }

        result = self.fixer._quick_fix_indentation(indentation_failure["file"])
        self.assertTrue(result)

        with open(indentation_failure["file"], "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("\t", content)  # Ensure tabs were replaced


if __name__ == "__main__":
    unittest.main()
