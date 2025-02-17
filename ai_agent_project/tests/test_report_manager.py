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
        cls.test_filename = "test_report.json"

    def setUp(self):
        """Prepare a clean test environment before each test."""
        self.manager.save_report("test_report", self.test_data)

    def tearDown(self):
        """Clean up test artifacts after each test."""
        # Close the logger to prevent file locks
        logging.shutdown()

        for file in os.listdir(self.manager.REPORTS_DIR):
            file_path = os.path.join(self.manager.REPORTS_DIR, file)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except PermissionError:
                    print(f"⚠️ Could not delete {file_path}, skipping...")

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
        self.assertEqual(loaded_data.get("status"), "success", "Report content mismatch.")  # Fixed expected value

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

    @patch("os.remove")
    def test_delete_old_reports(self, mock_remove):
        """Test deleting reports older than a certain threshold."""
        mock_remove.return_value = None
        self.manager.delete_old_reports(days=0)
        mock_remove.assert_called()

    @patch("report_manager.logging.FileHandler")
    def test_log_entry(self, mock_file_handler):
        """Test logging system with different levels."""
        self.manager.log_entry("Test INFO log")
        self.manager.log_entry("Test ERROR log", level="error")

        self.assertTrue(mock_file_handler.called, "Log file handler was not initialized.")

    def test_log_rotation(self):
        """Test log rotation mechanism to prevent oversized log files."""
        log_file = self.manager.LOG_FILE
        with open(log_file, "w") as f:
            f.write("X" * (self.manager.MAX_LOG_SIZE + 1))  # Simulate oversized log
        
        logging.shutdown()  # Ensure file is released before renaming
        self.manager._setup_logging()  # Trigger rotation

        rotated_log = f"{log_file}.1"
        self.assertTrue(os.path.exists(rotated_log), "Log rotation did not occur.")

if __name__ == "__main__":
    unittest.main()
