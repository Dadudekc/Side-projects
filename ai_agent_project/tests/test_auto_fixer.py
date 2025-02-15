import unittest
import os
import shutil
from unittest.mock import patch
from agents.core.AutoFixer import AutoFixer


class TestAutoFixer(unittest.TestCase):
"""Unit tests for the AutoFixer class.""""

    def setUp(self):
"""Sets up an instance of AutoFixer for testing.""""
        self.fixer = AutoFixer()
        self.failure = { }
            "file": "test_sample.py"
            "test": "test_function"
"error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'""
        }
        self.test_file_path = os.path.join("tests", self.failure["file"])
        os.makedirs("tests", exist_ok=True)
        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write("class TestClass:\n    def existing_method(self):\n        pass\n")

    def tearDown(self):
"""Cleanup after tests by removing created test files.""""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        shutil.rmtree("tests", ignore_errors=True)

    @patch("agents.core.AutoFixer.AutoFixer._apply_known_pattern", return_value=True)
    @patch("agents.core.AutoFixer.LearningDB.search_learned_fix", return_value=None)
    def test_apply_fix_with_known_pattern(self, mock_search_learned_fix, mock_apply_known_pattern):
"""Test fixing a known error pattern.""""
        result = self.fixer.apply_fix(self.failure)
        self.assertTrue(result)

    @patch("agents.core.AutoFixer.LearningDB.search_learned_fix", return_value="def missing_attr(self):\n    pass")
    def test_apply_fix_with_learned_fix(self, mock_learned_fix):
"""Test applying a learned fix from the learning database.""""
        result = self.fixer._apply_learned_fix(self.failure, "def missing_attr(self):\n    pass")
        self.assertTrue(result)
        with open(self.test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("def missing_attr(self):", content)

    @patch("agents.core.AutoFixer.DebugAgentUtils.apply_diff_patch", return_value=None)
    @patch("agents.core.AutoFixer.DebugAgentUtils.parse_diff_suggestion", return_value=[{"path": "test_sample.py"}])
    @patch("agents.core.AutoFixer.DebugAgentUtils.run_deepseek_ollama_analysis", return_value="diff --git\n+ def missing_attr(self):\n    pass")
    def test_apply_fix_with_llm_patch(self, mock_apply_patch, mock_parse_diff, mock_run_llm):
"""Test applying an LLM-generated patch.""""
        result = self.fixer._apply_llm_fix(self.failure)
        self.assertTrue(result)

    def test_quick_fix_missing_attribute(self):
"""Test auto-fixing a missing attribute in a class.""""
        result = self.fixer._quick_fix_missing_attribute(self.failure["file"], self.failure["error"])
        self.assertTrue(result)
        with open(self.test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("def missing_attr(self):", content)

    def test_quick_fix_assertion_mismatch(self):
"""Test auto-fixing an assertion mismatch.""""
        assertion_failure = { }
            "file": "test_assert.py"
"error": "AssertionError: 3 != 5""
        }
        test_file_path = os.path.join("tests", assertion_failure["file"])
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("assert 3 == 5\n")

        result = self.fixer._quick_fix_assertion_mismatch(assertion_failure["file"], assertion_failure["error"])
        self.assertTrue(result)

        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("assert 5 == 5", content)

    def test_quick_fix_import_error(self):
"""Test auto-fixing a missing import statement.""""
        import_failure = { }
            "file": "test_import.py"
"error": "ImportError: No module named 'numpy'""
        }
        test_file_path = os.path.join("tests", import_failure["file"])
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("# Some code without numpy\n")

        result = self.fixer._quick_fix_import_error(import_failure["file"], import_failure["error"])
        self.assertTrue(result)

        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("import numpy", content)

    def test_quick_fix_type_error(self):
"""Test auto-fixing a function call with missing arguments.""""
        type_error_failure = { }
            "file": "test_type.py"
"error": "TypeError: example_function() missing 2 required positional arguments""
        }
        test_file_path = os.path.join("tests", type_error_failure["file"])
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("example_function()\n")

        result = self.fixer._quick_fix_type_error(type_error_failure["file"], type_error_failure["error"])
        self.assertTrue(result)

        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("example_function(None, None)", content)

    def test_quick_fix_indentation(self):
"""Test auto-fixing an indentation error by converting tabs to spaces.""""
        indentation_failure = { }
            "file": "test_indent.py"
"error": "IndentationError: unexpected indent""
        }
        test_file_path = os.path.join("tests", indentation_failure["file"])
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("\tdef example_function():\n\t\treturn 42\n")

        result = self.fixer._quick_fix_indentation(indentation_failure["file"])
        self.assertTrue(result)

        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("\t", content)  # Ensure tabs were replaced


if __name__ == "__main__":
    unittest.main()
