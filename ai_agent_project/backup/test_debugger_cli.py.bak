import argparse
import json
import os
import unittest
from unittest.mock import MagicMock, patch

from ai_engine.models.debugger.debugger_cli import AI_PERFORMANCE_FILE, DebuggerCLI


class TestDebuggerCLI(unittest.TestCase):
    """Unit tests for the DebuggerCLI class."""

    def setUp(self):
        """Sets up an instance of DebuggerCLI for testing."""
        self.cli = DebuggerCLI()
        self.test_file = "test_debug.py"
        self.test_ai_performance_data = {
            "2025-02-14": {
                "total_fixes": 10,
                "success_rate": 80,
                "ai_feedback": {"quality": 4.5, "accuracy": 90},
            }
        }

    def tearDown(self):
        """Cleans up any temporary test files."""
        if os.path.exists(AI_PERFORMANCE_FILE):
            os.remove(AI_PERFORMANCE_FILE)

    @patch("ai_engine.models.debugger.debugger_cli.os.path.exists", return_value=True)
    @patch("ai_engine.models.debugger.debugger_cli.json.load")
    @patch("builtins.open", create=True)
    def test_load_ai_performance(self, mock_open, mock_json_load, mock_exists):
        """Test loading AI performance data."""
        mock_json_load.return_value = self.test_ai_performance_data
        # Ensure that the context manager returns a mock file object.
        mock_open.return_value.__enter__.return_value = MagicMock()
        result = self.cli.load_ai_performance()
        self.assertEqual(result, self.test_ai_performance_data)

    @patch("ai_engine.models.debugger.debugger_cli.json.load", return_value={})
    @patch("builtins.open", create=True)
    def test_load_ai_performance_empty(self, mock_open, mock_json_load):
        """Test loading AI performance when no data exists."""
        # Let os.path.exists return False so the file is not "found."
        result = self.cli.load_ai_performance()
        self.assertEqual(result, {})

    def test_run_debugger_specific_file(self):
        """Test debugging a specific file."""
        # Patch the instance method on debugger_core.
        self.cli.debugger_core.debug_file = MagicMock(return_value="Debugging Successful")
        self.cli.run_debugger(self.test_file)
        self.cli.debugger_core.debug_file.assert_called_with(self.test_file)

    def test_run_debugger_full(self):
        """Test running the full debugging process."""
        self.cli.debugger_core.debug = MagicMock(return_value="Full Debugging Successful")
        self.cli.run_debugger()
        self.cli.debugger_core.debug.assert_called()

    def test_show_logs(self):
        """Test displaying debugging logs."""
        self.cli.debugger_core.show_logs = MagicMock()
        self.cli.show_logs()
        self.cli.debugger_core.show_logs.assert_called()

    def test_rollback_fixes(self):
        """Test rolling back fixes."""
        self.cli.debugger_core.get_last_modified_files = MagicMock(return_value=["file1.py", "file2.py"])
        self.cli.debugger_core.rollback_changes = MagicMock()
        self.cli.rollback_fixes()
        self.cli.debugger_core.get_last_modified_files.assert_called()
        self.cli.debugger_core.rollback_changes.assert_called_with(["file1.py", "file2.py"])

    def test_rollback_fixes_no_changes(self):
        """Test rolling back fixes when no modifications exist."""
        self.cli.debugger_core.get_last_modified_files = MagicMock(return_value=[])
        self.cli.rollback_fixes()
        self.cli.debugger_core.get_last_modified_files.assert_called()

    def test_fix_imports_no_errors(self):
        """Test checking for import errors when none exist."""
        # Directly set the instance attribute.
        self.cli.patch_tracker.import_fixes = {}
        self.cli.fix_imports()
        self.assertEqual(self.cli.patch_tracker.import_fixes, {})

    def test_fix_imports_with_errors(self):
        """Test checking for and fixing missing imports."""
        self.cli.patch_tracker.import_fixes = {"numpy": {"fixed": 1, "failed": 0}}
        self.cli.fix_imports()
        self.assertIn("numpy", self.cli.patch_tracker.import_fixes)

    @patch.object(DebuggerCLI, "run_debugger")
    @patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        debug=True, file="test_debug.py", logs=False, rollback=False, performance=False, fix_imports=False, verbose=False))
    def test_parse_arguments_debug_file(self, mock_parse_args, mock_run_debugger):
        """Test CLI argument parsing for debugging a specific file."""
        args = self.cli.parse_arguments()
        self.cli.execute_commands(args)
        mock_run_debugger.assert_called_with("test_debug.py")

    @patch.object(DebuggerCLI, "show_logs")
    @patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        debug=False, file=None, logs=True, rollback=False, performance=False, fix_imports=False, verbose=False))
    def test_parse_arguments_logs(self, mock_parse_args, mock_show_logs):
        """Test CLI argument parsing for displaying logs."""
        args = self.cli.parse_arguments()
        self.cli.execute_commands(args)
        mock_show_logs.assert_called()

    @patch.object(DebuggerCLI, "rollback_fixes")
    @patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        debug=False, file=None, logs=False, rollback=True, performance=False, fix_imports=False, verbose=False))
    def test_parse_arguments_rollback(self, mock_parse_args, mock_rollback_fixes):
        """Test CLI argument parsing for rollback fixes."""
        args = self.cli.parse_arguments()
        self.cli.execute_commands(args)
        mock_rollback_fixes.assert_called()

    @patch.object(DebuggerCLI, "show_ai_performance")
    @patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        debug=False, file=None, logs=False, rollback=False, performance=True, fix_imports=False, verbose=False))
    def test_parse_arguments_performance(self, mock_parse_args, mock_show_ai_performance):
        """Test CLI argument parsing for viewing AI performance."""
        args = self.cli.parse_arguments()
        self.cli.execute_commands(args)
        mock_show_ai_performance.assert_called()

    @patch.object(DebuggerCLI, "fix_imports")
    @patch("argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(
        debug=False, file=None, logs=False, rollback=False, performance=False, fix_imports=True, verbose=False))
    def test_parse_arguments_fix_imports(self, mock_parse_args, mock_fix_imports):
        """Test CLI argument parsing for fixing import errors."""
        args = self.cli.parse_arguments()
        self.cli.execute_commands(args)
        mock_fix_imports.assert_called()


if __name__ == "__main__":
    unittest.main()
