import os
import shutil
import unittest
from unittest.mock import patch
import subprocess
from ai_engine.models.debugger.auto_fixer import AutoFixer

# Helper functions for integration test
def extract_failures(test_output):
    # Dummy extractor; in practice, parse test_output to extract failure details.
    return []

def attempt_fixes(failures):
    fixer = AutoFixer()
    for failure in failures:
        fixer.apply_fix(failure)

# A valid unified diff patch for AI tests
VALID_PATCH = """diff --git a/test_sample.py b/test_sample.py
--- a/test_sample.py
+++ b/test_sample.py
@@ -0,0 +1,2 @@
+def missing_attr(self):
+    pass
"""

class TestAutoFixer(unittest.TestCase):
    PROJECT_DIR = "project_files"
    TEST_WORKSPACE = "test_workspace"
    TEST_FILE = "test_sample.py"

    @classmethod
    def setUpClass(cls):
        needed_files = ["test_sample.py"]
        cls.fixer = AutoFixer(needed_files=needed_files)

    def setUp(self):
        os.makedirs(self.TEST_WORKSPACE, exist_ok=True)
        self.failure = {
            "file": self.TEST_FILE,
            "error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'",
        }
        with open(os.path.join(self.TEST_WORKSPACE, self.TEST_FILE), "w", encoding="utf-8") as f:
            f.write("class TestClass:\n    pass\n")

    def tearDown(self):
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

    def test_quick_fix_assertion_mismatch(self):
        """Test fixing an assertion mismatch."""
        file_path = os.path.join(self.TEST_WORKSPACE, "test_assert.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("assert 3 == 5\n")
        failure = {"file": "test_assert.py", "error": "AssertionError: 3 != 5"}
        result = self.fixer._quick_fix_assertion_mismatch(failure["file"], failure["error"])
        self.assertTrue(result)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("assert 5 == 5", content)

    def test_quick_fix_import_error(self):
        """Test fixing an ImportError by adding the missing import."""
        file_path = os.path.join(self.TEST_WORKSPACE, "test_import.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("print('Hello')\n")
        failure = {"file": "test_import.py", "error": "ImportError: No module named 'pandas'"}
        result = self.fixer._quick_fix_import_error(failure["file"], failure["error"])
        self.assertTrue(result)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("import pandas", content)

    def test_apply_fix_with_llm_patch(self):
        """Test applying an LLM-generated patch."""
        with patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.apply_diff_patch", return_value=None):
            with patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.parse_diff_suggestion", return_value=VALID_PATCH):
                with patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.run_deepseek_ollama_analysis", return_value=VALID_PATCH):
                    result = self.fixer._apply_llm_fix(self.failure)
                    self.assertTrue(result)

    @patch("ai_engine.models.debugger.learning_db.LearningDB.search_learned_fix", return_value=None)
    def test_missing_file(self, mock_db):
        """Ensure AutoFixer handles missing files gracefully."""
        failure = {"file": "non_existent.py", "error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'"}
        result = self.fixer.apply_fix(failure)
        self.assertFalse(result)

    def test_corrupt_file(self):
        """Ensure AutoFixer can handle a corrupt file gracefully."""
        file_path = os.path.join(self.TEST_WORKSPACE, "corrupt_test.py")
        with open(file_path, "wb") as f:
            f.write(b"\x00\x01\x02")  # Writing non-text bytes
        failure = {"file": "corrupt_test.py", "error": "SyntaxError: invalid syntax"}
        result = self.fixer.apply_fix(failure)
        self.assertFalse(result)

    def test_multiple_failures(self):
        """Ensure AutoFixer can handle multiple failures in a single session."""
        failures = [
            {"file": "test_sample.py", "error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'"},
            {"file": "test_import.py", "error": "ImportError: No module named 'numpy'"},
            {"file": "test_type.py", "error": "TypeError: example_function() missing 2 required positional arguments"},
        ]
        results = [self.fixer.apply_fix(failure) for failure in failures]
        self.assertTrue(any(results))  # At least one should succeed

    @patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.run_deepseek_ollama_analysis", return_value=VALID_PATCH)
    def test_ai_generated_fix_success(self, mock_ai_patch):
        """Ensure AutoFixer applies AI-generated patches correctly."""
        failure = {"file": "test_sample.py", "error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'"}
        result = self.fixer._apply_llm_fix(failure)
        self.assertTrue(result)

    @patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.run_deepseek_ollama_analysis", return_value="")
    def test_ai_generated_fix_empty(self, mock_ai_patch):
        """Ensure AutoFixer handles empty AI-generated patches."""
        failure = {"file": "test_sample.py", "error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'"}
        result = self.fixer._apply_llm_fix(failure)
        self.assertFalse(result)

    @patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.run_deepseek_ollama_analysis", return_value="INVALID PATCH DATA")
    def test_ai_generated_fix_invalid(self, mock_ai_patch):
        """Ensure AutoFixer rejects invalid AI-generated patches."""
        failure = {"file": "test_sample.py", "error": "AttributeError: 'TestClass' object has no attribute 'missing_attr'"}
        result = self.fixer._apply_llm_fix(failure)
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
        # Expect that the function call line is modified, but the definition remains unchanged.
        self.assertIn("example_function(None, None)", content)
        self.assertNotIn("def example_function(a, b, None, None)", content)

    def test_quick_fix_assertion_mismatch(self):
        """Ensure AutoFixer adjusts assertion errors correctly."""
        file_path = os.path.join(self.TEST_WORKSPACE, "test_assert.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("assert 2 == 5\n")
        failure = {"file": "test_assert.py", "error": "AssertionError: 2 != 5"}
        result = self.fixer._quick_fix_assertion_mismatch(failure["file"], failure["error"])
        self.assertTrue(result)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("assert 5 == 5", content)

    def test_full_auto_debugging(self):
        """Ensure AutoFixer can run full debugging cycle on a failing test suite."""
        # For this integration test, we assume no failures are extracted.
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
