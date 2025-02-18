"""

This module contains the unit tests for the ReportManager class which is used for managing debugging reports in an AI engine. 

The test suite includes functions to test the creation, load, deletion and listing of debug reports. There are also function to test for deleting old reports based on the number of days specified and to search reports by specified keyword.

The setUp method is responsible for creating a ReportManager instance along with dummy report content for testing. The tearDown method cleans up the generated report files and releases their
"""

import os
import json
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from ai_engine.models.debugger.report_manager import ReportManager
import logging

class TestReportManager(unittest.TestCase):
    """Unit tests for ReportManager."""

    def setUp(self):
        """Set up a fresh instance of ReportManager for each test."""
        self.manager = ReportManager()
        self.test_report_data = {
            "test_name": "AI Model Test",
            "status": "passed",
            "timestamp": datetime.now().isoformat(),
            "details": {"accuracy": 0.95, "time_elapsed": "3.2s"}
        }
        self.test_filename = "test_report.json"
        self.test_filepath = os.path.join(self.manager.REPORTS_DIR, self.test_filename)

    def tearDown(self):
        """Cleanup generated test reports and release file locks."""
        # Ensure all handlers are removed after each test
        for handler in self.manager.logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                self.manager.logger.removeHandler(handler)

        # Now delete the files safely
        if os.path.exists(self.manager.REPORTS_DIR):
            for file in os.listdir(self.manager.REPORTS_DIR):
                file_path = os.path.join(self.manager.REPORTS_DIR, file)
                try:
                    os.remove(file_path)
                except PermissionError:
                    print(f"Warning: Could not delete {file_path} (file in use)")

            os.rmdir(self.manager.REPORTS_DIR)

    def test_save_report(self):
        """Test saving a JSON report."""
        self.manager.save_report("test_report", self.test_report_data)

        # Check if the report exists
        saved_files = self.manager.list_reports()
        self.assertTrue(any("test_report" in filename for filename in saved_files))

        # Check if file content matches expected data
        with open(os.path.join(self.manager.REPORTS_DIR, saved_files[0]), "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, self.test_report_data)

    def test_load_report(self):
        """Test loading a JSON report."""
        self.manager.save_report("test_report", self.test_report_data)
        saved_files = self.manager.list_reports()
        loaded_data = self.manager.load_report(saved_files[0])
        self.assertEqual(loaded_data, self.test_report_data)

    def test_load_nonexistent_report(self):
        """Test attempting to load a non-existent report."""
        self.assertIsNone(self.manager.load_report("nonexistent_report.json"))

    def test_list_reports(self):
        """Test listing available reports."""
        self.manager.save_report("test_report_1", self.test_report_data)
        self.manager.save_report("test_report_2", self.test_report_data)
        
        reports = self.manager.list_reports()
        self.assertEqual(len(reports), 2)
        self.assertTrue(any("test_report_1" in filename for filename in reports))
        self.assertTrue(any("test_report_2" in filename for filename in reports))

    def test_search_reports(self):
        """Test searching reports by keyword."""
        ai_report = {
            "test_name": "AI Model Evaluation",
            "status": "passed",
            "timestamp": datetime.now().isoformat(),
            "details": {"accuracy": 0.95, "time_elapsed": "3.2s", "summary": "AI performed well."}
        }
        debug_report = {
            "test_name": "System Debugging",
            "status": "passed",
            "timestamp": datetime.now().isoformat(),
            "details": {"issues_found": 2, "resolved": True, "summary": "Debugging complete."}
        }

        self.manager.save_report("ai_test_report", ai_report)
        self.manager.save_report("debug_log", debug_report)

        search_results = self.manager.search_reports("AI")
        
        # ✅ Check if any file in search_results starts with "ai_test_report"
        self.assertTrue(any(filename.startswith("ai_test_report") for filename in search_results))

        # ✅ Ensure "debug_log" is excluded
        self.assertFalse(any(filename.startswith("debug_log") for filename in search_results))



    @patch("os.remove")
    def test_delete_old_reports(self, mock_remove):
        """Test deleting reports older than a specific number of days."""
        # Create an old test file
        old_filename = "old_report.json"
        old_filepath = os.path.join(self.manager.REPORTS_DIR, old_filename)
        os.makedirs(self.manager.REPORTS_DIR, exist_ok=True)
        with open(old_filepath, "w") as f:
            json.dump(self.test_report_data, f)

        # Set modification time to 40 days ago
        old_timestamp = datetime.now().timestamp() - (40 * 86400)
        os.utime(old_filepath, (old_timestamp, old_timestamp))

        # Delete old reports
        self.manager.delete_old_reports(days=30)

        # Ensure file removal was attempted
        mock_remove.assert_called_once_with(old_filepath)

    def test_log_entry(self):
        """Test structured logging of a message."""
        with patch.object(self.manager.logger, "info") as mock_logger:
            self.manager.log_entry("Test log entry")
            mock_logger.assert_called_with("Test log entry")


if __name__ == "__main__":
    unittest.main()
