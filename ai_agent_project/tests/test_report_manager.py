"""

A module that contains a unittest class, TestReportManager, to test the functionality of ReportManager.

The class contains set up and tear down methods that sets up the testing environment and cleans up after every test.

Test methods included in the class:
- test_save_report: Verifies that a JSON report saved using the class 'ReportManager'.
- test_load_report: Verifies that a report saved using the class 'ReportManager' is loadable and its contents are as expected.
- test_list
"""

import os
import json
import unittest
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock
from ai_engine.models.debugger.report_manager import ReportManager

class TestReportManager(unittest.TestCase):
    """Unit tests for ReportManager functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment before all tests."""
        cls.manager = ReportManager()
        cls.test_data = {
            "test_name": "Sample Report",
            "status": "success",  # Fixed expected value
            "timestamp": datetime.now().isoformat()
        }

    def setUp(self):
        """Ensure 'reports/' directory exists and save an initial report."""
        os.makedirs(self.manager.REPORTS_DIR, exist_ok=True)
        self.manager.save_report("test_report", self.test_data)

    def tearDown(self):
        """Safely remove reports and log handlers after tests."""
        for handler in self.manager.logger.handlers[:]:
            handler.close()
            self.manager.logger.removeHandler(handler)

        if os.path.exists(self.manager.REPORTS_DIR):
            for file in os.listdir(self.manager.REPORTS_DIR):
                file_path = os.path.join(self.manager.REPORTS_DIR, file)
                try:
                    os.remove(file_path)
                except PermissionError:
                    print(f"⚠️ Warning: Could not delete {file_path} (file in use).")

        try:
            os.rmdir(self.manager.REPORTS_DIR)
        except OSError:
            print(f"⚠️ Warning: Could not remove {self.manager.REPORTS_DIR} (not empty).")

    def test_save_report(self):
        """Test saving a JSON report."""
        test_file = "ai_test_report"
        self.manager.save_report(test_file, self.test_data)
        files = os.listdir(self.manager.REPORTS_DIR)
        self.assertTrue(any(test_file in f for f in files), "Report file not saved.")

    def test_load_report(self):
        """Test loading an existing report."""
        reports = self.manager.list_reports()
        self.assertTrue(reports, "No reports found.")

        loaded_data = self.manager.load_report(reports[0])
        self.assertIsInstance(loaded_data, dict, "Loaded report should be a dictionary.")
        self.assertEqual(loaded_data.get("status"), "success", "Report content mismatch.")

    def test_list_reports(self):
        """Test listing available reports."""
        reports = self.manager.list_reports()
        self.assertGreaterEqual(len(reports), 1, "Report listing failed.")

    def test_search_reports_by_filename(self):
        """Test searching reports by filename."""
        matches = self.manager.search_reports("test_report")
        self.assertGreaterEqual(len(matches), 1, "Search should return at least one match.")

    def test_search_reports_by_content(self):
        """Test searching reports by content (keyword inside JSON data)."""
        matches = self.manager.search_reports("Sample Report")
        self.assertGreaterEqual(len(matches), 1, "Search should return at least one match.")

    @patch("ai_engine.models.debugger.report_manager.os.remove")
    @patch("ai_engine.models.debugger.report_manager.os.path.getmtime")
    def test_delete_old_reports(self, mock_getmtime, mock_remove):
        """Test deleting reports older than a certain threshold."""
        mock_getmtime.return_value = 0  # Simulate old reports
        self.manager.delete_old_reports(days=0)
        self.assertTrue(mock_remove.called, "Old reports were not deleted.")

    @patch.object(logging, "getLogger")
    def test_log_entry(self, mock_get_logger):
        """Test logging system with different levels."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger  # Mock the logger instance

        self.manager.logger = mock_logger  # Replace the instance's logger with the mock

        self.manager.log_entry("Test INFO log")
        self.manager.log_entry("Test ERROR log", level="error")

        # ✅ Validate that the correct logging calls were made
        mock_logger.info.assert_any_call("Test INFO log")
        mock_logger.error.assert_any_call("Test ERROR log")


    def test_log_rotation(self):
        """Test log rotation mechanism to prevent oversized log files."""
        log_file = self.manager.LOG_FILE
        os.makedirs(self.manager.REPORTS_DIR, exist_ok=True)  # Ensure directory exists

        with open(log_file, "w") as f:
            f.write("X" * (self.manager.MAX_LOG_SIZE + 1))  # Simulate oversized log
        
        logging.shutdown()  # Ensure file is released before renaming
        self.manager._setup_logging()  # Trigger rotation

        rotated_log = f"{log_file}.1"
        self.assertTrue(os.path.exists(rotated_log), "Log rotation did not occur.")


if __name__ == "__main__":
    unittest.main()
