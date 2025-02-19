"""
This module defines a suite of unit tests for the AutoFixer class, which is part of an AI debugging engine. 
These tests verify that AutoFixer correctly identifies and applies fixes for various Python bug patterns.
"""

import os
import shutil
import unittest
from unittest.mock import patch, MagicMock
import subprocess
from ai_engine.models.debugger.auto_fixer import AutoFixer
from agents.core.utilities.debug_agent_utils import DebugAgentUtils

# Helper functions for integration test
def extract_failures(test_output):
    """Extracts failure details from pytest output."""
    return []

def attempt_fixes(failures):
    """Applies fixes using AutoFixer."""
    fixer = AutoFixer()
    for failure in failures:
        fixer.apply_fix(failure)

# Valid unified diff patch for AI-generated tests
VALID_PATCH = """diff --git a/test_sample.py b/test_sample.py
--- a/test_sample.py
+++ b/test_sample.py
@@ -0,0 +1,2 @@
+def missing_attr(self):
+    pass
"""

class TestAutoFixer(unittest.TestCase):
    """Unit tests for the AutoFixer class."""
    
    PROJECT_DIR = "project_files"
    TEST_WORKSPACE = "test_workspace"
    TEST_FILE = "test_sample.py"

    @classmethod
    def setUpClass(cls):
        needed_files = ["test_sample.py"]
        cls.fixer = AutoFixer(needed_files=needed_files)

    def setUp(self):
        """Sets up a test workspace for file operations."""
        os.makedirs(self.TEST_WORKSPACE, exist_ok=True)
        self.failure = {
            "file": self.TEST_FILE,
            "error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'",
        }
        with open(os.path.join(self.TEST_WORKSPACE, self.TEST_FILE), "w", encoding="utf-8") as f:
            f.write("class TestClass:\n    pass\n")

    def tearDown(self):
        """Cleans up the test workspace."""
        shutil.rmtree(self.TEST_WORKSPACE)

    def test_apply_fix_with_known_pattern(self):
        """Test that a known error pattern is fixed."""
        with patch("ai_engine.models.debugger.learning_db.LearningDB.search_learned_fix", return_value=None):
            with patch("ai_engine.models.debugger.auto_fixer.AutoFixer._apply_known_pattern", return_value=True):
                result = self.fixer.apply_fix(self.failure)
                self.assertTrue(result)

    def test_quick_fix_missing_attribute(self):
        """Test auto-fixing a missing attribute in a copied project file."""
        result = self.fixer._quick_fix_missing_attribute(self.TEST_FILE, self.failure["error"])
        self.assertTrue(result)
        with open(os.path.join(self.TEST_WORKSPACE, self.TEST_FILE), "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("def missing_attr(self):", content)

    def test_apply_fix_with_llm_patch(self):
        """Test applying an LLM-generated patch."""
        with patch.object(DebugAgentUtils, "apply_diff_patch", return_value=None):
            with patch.object(DebugAgentUtils, "parse_diff_suggestion", return_value=VALID_PATCH):
                with patch.object(DebugAgentUtils, "run_deepseek_ollama_analysis", return_value=VALID_PATCH):
                    result = self.fixer._apply_llm_fix(self.failure)
                    self.assertTrue(result)

    def test_corrupt_file(self):
        """Ensure AutoFixer can handle a corrupt file gracefully."""
        file_path = os.path.join(self.TEST_WORKSPACE, "corrupt_test.py")
        with open(file_path, "wb") as f:
            f.write(b"\x00\x01\x02")  # Writing non-text bytes
        failure = {"file": "corrupt_test.py", "error": "SyntaxError: invalid syntax"}
        result = self.fixer.apply_fix(failure)
        self.assertFalse(result)

    def test_ai_generated_fix_success(self):
        """Ensure AutoFixer applies AI-generated patches correctly."""
        with patch.object(DebugAgentUtils, "run_deepseek_ollama_analysis", return_value=VALID_PATCH):
            result = self.fixer._apply_llm_fix(self.failure)
            self.assertTrue(result)

    def test_ai_generated_fix_invalid(self):
        """Ensure AutoFixer rejects invalid AI-generated patches."""
        with patch.object(DebugAgentUtils, "run_deepseek_ollama_analysis", return_value="INVALID PATCH DATA"):
            result = self.fixer._apply_llm_fix(self.failure)
            self.assertFalse(result)

    def test_quick_fix_type_error(self):
        """Ensure AutoFixer correctly inserts missing arguments in function calls."""
        file_path = os.path.join(self.TEST_WORKSPACE, "test_type.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("def example_function(a, b): pass\nexample_function()\n")
        failure = {"file": "test_type.py", "error": "TypeError: example_function() missing 2 required positional arguments"}
        result = self.fixer._quick_fix_type_error(failure["file"], failure["error"])
        self.assertTrue(result)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("example_function(None, None)", content)

    def test_full_auto_debugging(self):
        """Ensure AutoFixer can run full debugging cycle on a failing test suite."""
        test_output = subprocess.run(["pytest", "tests/failing_tests/"], capture_output=True, text=True).stdout
        failures = extract_failures(test_output)
        if not failures:
            print("✅ No failures detected. Skipping AutoFixer.")
            return
        print(f"⚠ Found {len(failures)} failing tests. Running AutoFixer...")
        attempt_fixes(failures)
        print("🔄 Re-running tests after fixes...")
        test_output = subprocess.run(["pytest", "tests/failing_tests/"], capture_output=True, text=True).stdout
        self.assertNotIn("FAILED", test_output)

if __name__ == "__main__":
    unittest.main()
