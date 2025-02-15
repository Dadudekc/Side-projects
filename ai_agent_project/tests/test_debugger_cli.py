import unittest
import os
import json
from unittest.mock import patch, MagicMock
from agents.core.core import DebuggerCLI import DebuggerCLI, AI_PERFORMANCE_FILE


class TestDebuggerCLI(unittest.TestCase):
"""""
"""    Unit tests for the DebuggerCLI class. """"    """ """""""
"    def setUp(self):""
"        """ """"""        Sets up an instance of DebuggerCLI for testing.
"        """ """""        self.cli = DebuggerCLI()""
"        self.test_file = "test_debug.py"""
"        self.test_ai_performance_data = {"            "2025-02-14": { }
                "total_fixes": 10
                "success_rate": 80
                "ai_feedback": {"quality": 4.5, "accuracy": 90}
            }
        }

    def tearDown(self):
""" """"""        Cleans up any temporary test files. """"        """"
""        if os.path.exists(AI_PERFORMANCE_FILE):
"            os.remove(AI_PERFORMANCE_FILE)""
"""
    @patch("agents.core.DebuggerCLI.json.load")
    @patch("agents.core.DebuggerCLI.open", create=True)
    def test_load_ai_performance(self, mock_open, mock_json_load):
""" """"""        Test loading AI performance data. """"        """ """""        mock_json_load.return_value = self.test_ai_performance_data""        mock_open.return_value.__enter__.return_value = MagicMock()""
""        result = self.cli.load_ai_performance()
        self.assertEqual(result, self.test_ai_performance_data)

    @patch("agents.core.DebuggerCLI.json.load", return_value={})
    @patch("agents.core.DebuggerCLI.open", create=True)
    def test_load_ai_performance_empty(self, mock_open, mock_json_load):
"""""
"""        Test loading AI performance when no data exists. """"        """ """""        result = self.cli.load_ai_performance()""
"        self.assertEqual(result, {})""""
    @patch("agents.core.DebuggerCLI.DebuggerCore.debug_file", return_value="Debugging Successful")
    def test_run_debugger_specific_file(self, mock_debug_file):
""" """"""        Test debugging a specific file.""
"        """ """""        self.cli.run_debugger(self.test_file)""
"        mock_debug_file.assert_called_with(self.test_file)""
""    @patch("agents.core.DebuggerCLI.DebuggerCore.debug", return_value="Full Debugging Successful")
    def test_run_debugger_full(self, mock_debug):
""" """"""        Test running the full debugging process. """"        """"
""        self.cli.run_debugger()
"        mock_debug.assert_called()""
"""
    @patch("agents.core.DebuggerCLI.DebuggerCore.show_logs")
    def test_show_logs(self, mock_show_logs):
""" """"""        Test displaying debugging logs. """"        """ """""        self.cli.show_logs()""        mock_show_logs.assert_called()""
""    @patch("agents.core.DebuggerCLI.DebuggerCore.get_last_modified_files", return_value=["file1.py", "file2.py"])
    @patch("agents.core.DebuggerCLI.DebuggerCore.rollback_changes")
    def test_rollback_fixes(self, mock_rollback_changes, mock_get_last_modified_files):
"""""
"""        Test rolling back fixes. """"        """ """""        self.cli.rollback_fixes()""
"        mock_get_last_modified_files.assert_called()""        mock_rollback_changes.assert_called_with(["file1.py", "file2.py"])""

    @patch("agents.core.DebuggerCLI.DebuggerCore.get_last_modified_files", return_value=[])
    def test_rollback_fixes_no_changes(self, mock_get_last_modified_files):
""" """"""        Test rolling back fixes when no modifications exist.""
"        """ """""        self.cli.rollback_fixes()""
"        mock_get_last_modified_files.assert_called()""
""    @patch("agents.core.DebuggerCLI.PatchTrackingManager.import_fixes", return_value={})
    def test_fix_imports_no_errors(self, mock_import_fixes):
""" """"""        Test checking for import errors when none exist. """"        """"
""        self.cli.fix_imports()
"        mock_import_fixes.assert_called()""
"""
    @patch("agents.core.DebuggerCLI.PatchTrackingManager.import_fixes", return_value={"numpy": {"fixed": 1, "failed": 0}})
    def test_fix_imports_with_errors(self, mock_import_fixes):
""" """"""        Test checking for and fixing missing imports. """"        """ """""        self.cli.fix_imports()""        mock_import_fixes.assert_called()""
""    @patch("agents.core.DebuggerCLI.DebuggerCLI.run_debugger")
    @patch("agents.core.DebuggerCLI.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(debug=True, file="test_debug.py"))
    def test_parse_arguments_debug_file(self, mock_parse_args, mock_run_debugger):
"""""
"""        Test CLI argument parsing for debugging a specific file. """"        """ """""        self.cli.parse_arguments()""
"        mock_run_debugger.assert_called_with("test_debug.py")""""
    @patch("agents.core.DebuggerCLI.DebuggerCLI.show_logs")
    @patch("agents.core.DebuggerCLI.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(logs=True))
    def test_parse_arguments_logs(self, mock_parse_args, mock_show_logs):
""" """"""        Test CLI argument parsing for displaying logs.""
"        """ """""        self.cli.parse_arguments()""
"        mock_show_logs.assert_called()""
""    @patch("agents.core.DebuggerCLI.DebuggerCLI.rollback_fixes")
    @patch("agents.core.DebuggerCLI.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(rollback=True))
    def test_parse_arguments_rollback(self, mock_parse_args, mock_rollback_fixes):
""" """"""        Test CLI argument parsing for rollback fixes. """"        """"
""        self.cli.parse_arguments()
"        mock_rollback_fixes.assert_called()""
"""
    @patch("agents.core.DebuggerCLI.DebuggerCLI.show_ai_performance")
    @patch("agents.core.DebuggerCLI.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(performance=True))
    def test_parse_arguments_performance(self, mock_parse_args, mock_show_ai_performance):
""" """"""        Test CLI argument parsing for viewing AI performance. """"        """ """""        self.cli.parse_arguments()""        mock_show_ai_performance.assert_called()""
""    @patch("agents.core.DebuggerCLI.DebuggerCLI.fix_imports")
    @patch("agents.core.DebuggerCLI.argparse.ArgumentParser.parse_args", return_value=argparse.Namespace(fix_imports=True))
    def test_parse_arguments_fix_imports(self, mock_parse_args, mock_fix_imports):
"""""
"""        Test CLI argument parsing for fixing import errors. """"        """ """""        self.cli.parse_arguments()""
"        mock_fix_imports.assert_called()""""
if __name__ == "__main__":
    unittest.main()
