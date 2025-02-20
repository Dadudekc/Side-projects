import os
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch, call

from ai_engine.models.debugger.debugger_core import DebugAgent
class TestDebugAgent(unittest.TestCase):
    """Unit tests for the DebugAgent class."""

    def setUp(self):
        """Set up DebugAgent instance for testing."""
        self.agent = DebugAgent()

    # ========================
    # TEST: CORE FUNCTIONALITY
    # ========================

    def test_analyze_error(self):
        """Test analyzing error messages."""
        result = self.agent.analyze_error("TestError", context={"detail": "unit test"})
        self.assertIn("TestError", result)
        self.assertIn("unit test", result)

    def test_run_diagnostics(self):
        """Test running diagnostics."""
        result = self.agent.run_diagnostics(system_check=True, detailed=True)
        self.assertIn("Basic diagnostics", result)
        self.assertIn("System check passed", result)

    def test_describe_capabilities(self):
        """Test capability description."""
        result = self.agent.describe_capabilities()
        self.assertIn("run tests", result)
        self.assertIn("analyze errors", result)
        self.assertIn("automate debugging", result)

    # ========================
    # TEST: LEARNING DB
    # ========================

    def test_learning_db(self):
        """Test storing and retrieving fixes from learning DB."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_db = os.path.join(temp_dir, "learning_db.json")
            self.agent.LEARNING_DB_PATH = temp_db
            self.agent.learning_db = {}

            # Store a fix
            self.agent._store_learned_fix("SampleError", "SampleFix")
            self.assertIn("SampleError", self.agent.learning_db)
            self.assertEqual(self.agent.learning_db["SampleError"], "SampleFix")

            # Reload DB and verify
            new_agent = DebugAgent()
            new_agent.LEARNING_DB_PATH = temp_db
            loaded_db = new_agent._load_learning_db()
            self.assertIn("SampleError", loaded_db)
            self.assertEqual(loaded_db["SampleError"], "SampleFix")

    # ========================
    # TEST: RUNNING TESTS
    # ========================

    @patch("subprocess.run")
    def test_run_tests(self, mock_subprocess):
        """Test running all tests."""
        mock_subprocess.return_value.stdout = "Test output"
        mock_subprocess.return_value.stderr = ""  # Ensure stderr isn't interfering
        result = self.agent.run_tests()
        self.assertIn("Test output", result)

    @patch("subprocess.run")
    def test_run_tests_for_files(self, mock_subprocess):
        """Test running tests for specific files."""
        mock_subprocess.return_value.stdout = "File-specific output"
        mock_subprocess.return_value.stderr = ""  # Ensure stderr doesn't break it
        result = self.agent.run_tests_for_files({"test_file.py"})
        self.assertIn("File-specific output", result)

    def test_parse_test_failures(self):
        """Test parsing pytest output for failures."""
        sample_output = "FAILED test_file.py::test_example - AssertionError: Expected 5, got 10"
        failures = self.agent.parse_test_failures(sample_output)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["file"], "test_file.py")
        self.assertEqual(failures[0]["test"], "test_example")
        self.assertEqual(failures[0]["error"], "AssertionError: Expected 5, got 10")

    # ========================
    # TEST: APPLYING FIXES
    # ========================

    @patch.object(DebugAgent, "_apply_known_pattern", return_value=True)
    def test_apply_fix_known_pattern(self, mock_known_pattern):
        """Test applying fix via known error pattern."""
        failure = {"file": "test_file.py", "test": "test_func", "error": "AssertionError"}
        result = self.agent.apply_fix(failure)
        self.assertTrue(result)
        mock_known_pattern.assert_called_once_with(failure)

    @patch.object(DebugAgent, "_apply_known_pattern", return_value=False)
    @patch.object(DebugAgent, "_apply_adaptive_learning_fix", return_value=True)
    def test_apply_fix_adaptive_learning(self, mock_adaptive_fix, mock_known_pattern):
        """Test applying fix using adaptive learning when known pattern fails."""
        failure = {"file": "test_file.py", "test": "test_func", "error": "UnknownError"}
        result = self.agent.apply_fix(failure)
        self.assertTrue(result)
        mock_known_pattern.assert_called_once()
        mock_adaptive_fix.assert_called_once()

    @patch.object(DebugAgent, "_apply_known_pattern", return_value=False)
    @patch.object(DebugAgent, "_apply_adaptive_learning_fix", return_value=False)
    def test_apply_fix_failure(self, mock_adaptive_fix, mock_known_pattern):
        """Test failure scenario when no fix is applicable."""
        failure = {"file": "test_file.py", "test": "test_func", "error": "CriticalError"}
        result = self.agent.apply_fix(failure)
        self.assertFalse(result)
        mock_known_pattern.assert_called_once()
        mock_adaptive_fix.assert_called_once()

    # ========================
    # TEST: RETRYING FIXES
    # ========================

    @patch.object(DebugAgent, "run_tests", side_effect=[
        "FAILED test_file.py::test_func - Error",  # First attempt fails
        "",  # Second attempt passes (no failures)
    ])
    @patch.object(DebugAgent, "apply_fix", return_value=True)  # Fixes the issue
    @patch.object(DebugAgent, "push_to_github")
    def test_retry_tests_success(self, mock_push, mock_apply_fix, mock_run_tests):
        """Test retrying tests and fixing failures."""
        result = self.agent.retry_tests(max_retries=2)
        self.assertEqual(result["status"], "success")  # Now it should succeed
        mock_apply_fix.assert_called()


    @patch.object(DebugAgent, "run_tests", return_value="FAILED test_file.py::test_func - Error")
    @patch.object(DebugAgent, "apply_fix", return_value=False)
    @patch.object(DebugAgent, "rollback_changes")
    def test_retry_tests_failure(self, mock_rollback, mock_apply_fix, mock_run_tests):
        """Test retrying tests but failing to fix issues."""
        result = self.agent.retry_tests(max_retries=2)
        self.assertEqual(result["status"], "error")
        mock_rollback.assert_called()

    # ========================
    # TEST: GIT INTEGRATION
    # ========================

    @patch("subprocess.run")
    def test_push_to_github_success(self, mock_subprocess):
        """Test successful Git push."""
        self.agent.push_to_github("Test commit")
        mock_subprocess.assert_has_calls([
            call(["git", "add", "."], check=True),
            call(["git", "commit", "-m", "Test commit"], check=True),
            call(["git", "push"], check=True)
        ])

    @patch("subprocess.run", side_effect=Exception("Git error"))
    def test_push_to_github_failure(self, mock_subprocess):
        """Test handling Git push failure."""
        self.agent.push_to_github("Test commit")
        mock_subprocess.assert_called()

    # ========================
    # TEST: AUTOMATED DEBUGGING
    # ========================

    @patch.object(DebugAgent, "retry_tests", return_value={"status": "success"})
    def test_automate_debugging_success(self, mock_retry):
        """Test successful automated debugging."""
        result = self.agent.automate_debugging()
        self.assertEqual(result["status"], "success")
        mock_retry.assert_called_once()

    @patch.object(DebugAgent, "retry_tests", return_value={"status": "error"})
    def test_automate_debugging_failure(self, mock_retry):
        """Test automated debugging failure."""
        result = self.agent.automate_debugging()
        self.assertEqual(result["status"], "error")
        mock_retry.assert_called_once()


if __name__ == "__main__":
    unittest.main()
