import json
import os
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from ai_engine.models.debugger.debugger_core import DebuggerCore


class TestDebuggerCore(unittest.TestCase):
    """Unit tests for the DebuggerCore class."""

    def setUp(self):
        """Sets up an instance of DebuggerCore for testing."""
        self.debugger = DebuggerCore()
        self.test_file = "test_debug.py"
        self.learning_db_file = DebuggerCore.LEARNING_DB_FILE
        self.report_archive_dir = DebuggerCore.REPORT_ARCHIVE_DIR

    def tearDown(self):
        """Cleans up any temporary test files."""
        if os.path.exists(self.learning_db_file):
            os.remove(self.learning_db_file)
        if os.path.exists(self.report_archive_dir):
            for file in os.listdir(self.report_archive_dir):
                os.remove(os.path.join(self.report_archive_dir, file))
            os.rmdir(self.report_archive_dir)

    @patch("subprocess.run")
    def test_run_tests_simple(self, mock_subprocess):
        """Test running tests in simple mode."""
        mock_subprocess.return_value = MagicMock(
            stdout="test_debug.py - FAILED", returncode=1
        )
        result = self.debugger.run_tests_simple()
        self.assertIn("test_debug.py - FAILED", result)

    def test_parse_test_failures_simple(self):
        """Test parsing pytest output for failures."""
        test_output = "test_debug.py - FAILED\nanother_test.py - PASSED"
        failures = self.debugger.parse_test_failures_simple(test_output)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["file"], "test_debug.py")
        self.assertEqual(failures[0]["error"], "FAILED")

    @patch("subprocess.run")
    @patch("json.load")
    @patch("builtins.open", create=True)
    def test_run_tests_advanced(self, mock_open, mock_json_load, mock_subprocess):
        """Test running tests in advanced mode with pytest-json-report."""
        test_json_report = {
            "tests": [
                {
                    "nodeid": "test_debug.py::test_function",
                    "outcome": "failed",
                    "call": {"crash": {"message": "AssertionError"}},
                    "location": ["test_debug.py", "5"],
                }
            ]
        }

        mock_subprocess.return_value = MagicMock(returncode=1)
        mock_json_load.return_value = test_json_report

        errors = self.debugger.run_tests_advanced()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["test_filename"], "test_debug.py")

    def test_load_learning_db(self):
        """Test loading the learning database."""
        test_db_content = {
            "error_signature_1": {"attempts": 2, "patch": "sample_patch"}
        }
        with open(self.learning_db_file, "w", encoding="utf-8") as f:
            json.dump(test_db_content, f)

        loaded_db = self.debugger.load_learning_db()
        self.assertEqual(loaded_db, test_db_content)

    def test_save_learning_db(self):
        """Test saving the learning database."""
        test_db_content = {
            "error_signature_1": {"attempts": 2, "patch": "sample_patch"}
        }
        self.debugger.save_learning_db(test_db_content)

        with open(self.learning_db_file, "r", encoding="utf-8") as f:
            saved_db = json.load(f)

        self.assertEqual(saved_db, test_db_content)

    def test_compute_error_signature(self):
        """Test computing an error signature."""
        error_message = "Test failed due to assertion error"
        code_context = "assert expected == actual"
        signature = self.debugger.compute_error_signature(error_message, code_context)

        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 64)  # SHA-256 produces a 64-character hash

    @patch("subprocess.run")
    def test_re_run_tests(self, mock_subprocess):
        """Test re-running tests after applying a patch."""
        mock_subprocess.return_value = MagicMock(returncode=0)  # Simulate success
        result = self.debugger.re_run_tests()
        self.assertTrue(result)

        mock_subprocess.return_value = MagicMock(returncode=1)  # Simulate failure
        result = self.debugger.re_run_tests()
        self.assertFalse(result)

    def test_archive_report(self):
        """Test archiving JSON reports."""
        test_report_file = "report.json"
        with open(test_report_file, "w") as f:
            f.write("{}")

        self.debugger.archive_report(test_report_file)

        archived_files = os.listdir(self.report_archive_dir)
        self.assertEqual(len(archived_files), 1)

        os.remove(os.path.join(self.report_archive_dir, archived_files[0]))

    @patch("subprocess.run")
    def test_debug_simple(self, mock_subprocess):
        """Test debugging in simple mode."""
        mock_subprocess.return_value = MagicMock(
            stdout="test_debug.py - FAILED", returncode=1
        )
        with patch.object(self.debugger, "apply_fix", return_value=True):
            result = self.debugger._debug_simple(max_retries=1)
            self.assertEqual(result["status"], "success")

    @patch("subprocess.run")
    @patch("json.load")
    @patch("builtins.open", create=True)
    @patch.object(DebuggerCore, "apply_patch_to_file", return_value=True)
    @patch.object(DebuggerCore, "re_run_tests", return_value=True)
    def test_debug_advanced(
        self, mock_re_run, mock_apply_patch, mock_open, mock_json_load, mock_subprocess
    ):
        """Test debugging in advanced mode."""
        test_json_report = {
            "tests": [
                {
                    "nodeid": "test_debug.py::test_function",
                    "outcome": "failed",
                    "call": {"crash": {"message": "AssertionError"}},
                    "location": ["test_debug.py", "5"],
                }
            ]
        }

        mock_subprocess.return_value = MagicMock(returncode=1)
        mock_json_load.return_value = test_json_report

        result = self.debugger._debug_advanced()
        self.assertIsNone(result)

    def test_debug_with_unknown_mode(self):
        """Test handling of unknown debugging modes."""
        self.debugger.mode = "unknown"
        result = self.debugger.debug()
        self.assertEqual(result["status"], "error")

    def test_rollback_changes(self):
        """Test rolling back file changes."""
        test_file = "test_file.py"
        backup_file = f"{test_file}.backup"

        with open(test_file, "w") as f:
            f.write("original content")
        with open(backup_file, "w") as f:
            f.write("backup content")

        self.debugger.rollback_changes([test_file])

        with open(test_file, "r") as f:
            content = f.read()

        self.assertEqual(content, "backup content")

        os.remove(test_file)
        os.remove(backup_file)

    def test_show_logs(self):
        """Test displaying stored logs."""
        with patch.object(
            self.debugger.debugger_logger, "get_logs", return_value=["Test log entry"]
        ):
            with patch("agents.core.debugger_core.logger.info") as mock_logger:
                self.debugger.show_logs()
                mock_logger.assert_called_with("📝 Log Entry: Test log entry")


if __name__ == "__main__":
    unittest.main()
