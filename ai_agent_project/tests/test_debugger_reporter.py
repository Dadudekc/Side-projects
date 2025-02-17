import json
import os
from unittest.mock import MagicMock, patch

import pytest

from ai_engine.models.debugger.debugger_reporter import REPORT_FILE, DebuggerReporter
from ai_engine.models.debugger.email_reporter import EmailReporter


@pytest.fixture
def reporter():
    """Fixture to initialize DebuggerReporter instance."""
    return DebuggerReporter()


@pytest.fixture
def temp_report_file(tmp_path):
    """Creates a temporary debugging report file."""
    temp_file = tmp_path / "debugging_report.json"
    temp_file.write_text(json.dumps({"failed_patches": {}, "ai_explanations": {}}))
    return temp_file


# ** Test Initialization and Loading **
def test_initialize_report():
    """Test that a new report is created if no report exists."""
    if os.path.exists(REPORT_FILE):
        os.remove(REPORT_FILE)  # Ensure the report does not exist before the test

    reporter = DebuggerReporter()  # Initialize AFTER deleting report file

    assert isinstance(reporter.report_data, dict)
    assert "failed_patches" in reporter.report_data
    assert "ai_explanations" in reporter.report_data
    assert reporter.report_data["failed_patches"] == {}


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=MagicMock)
def test_load_existing_report(mock_open, mock_exists, reporter):
    """Test loading an existing debugging report without errors."""
    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
        {"failed_patches": {"hash1234": "Some failure"}, "ai_explanations": {}}
    )

    data = reporter.load_existing_report()
    assert "failed_patches" in data
    assert data["failed_patches"]["hash1234"] == "Some failure"


# ** Test Logging of Failed Patches and AI Explanations **
def test_log_failed_patch(reporter):
    """Test logging a failed patch."""
    reporter.log_failed_patch("hash5678", "Invalid syntax.")
    assert reporter.report_data["failed_patches"]["hash5678"] == "Invalid syntax."


def test_log_ai_explanation(reporter):
    """Test logging an AI explanation."""
    reporter.log_ai_explanation("hash1234", "Consider adding a missing import.")
    assert (
        reporter.report_data["ai_explanations"]["hash1234"]
        == "Consider adding a missing import."
    )


# ** Test Saving the Debugging Report **
@patch("builtins.open", new_callable=MagicMock)
def test_save_report(mock_open, reporter):
    """Test saving the debugging report to a JSON file."""
    reporter.log_failed_patch("hash5678", "SyntaxError detected.")
    reporter.save_report()

    mock_open.assert_called_once_with(REPORT_FILE, "w", encoding="utf-8")
    mock_open.return_value.__enter__().write.assert_called()


# ** Test Email Reporting with Mocks **
@patch("ai_engine.models.debugger.email_reporter.EmailReporter.send_debugging_report")
def test_send_email_report(mock_send_email, reporter):
    """Test sending an email report with a valid email."""
    mock_send_email.return_value = True  # Simulate successful email sending

    reporter.send_email_report("debugger@example.com")
    mock_send_email.assert_called_once_with(
        reporter.report_data, "debugger@example.com"
    )


@patch("ai_engine.models.debugger.email_reporter.EmailReporter.send_debugging_report")
@patch("ai_engine.models.debugger.debugger_reporter.logger.error")
def test_send_email_invalid_email(mock_logger_error, mock_send_email, reporter):
    """Test that an invalid email prevents sending a report and logs an error."""
    reporter.send_email_report("invalid-email")

    mock_send_email.assert_not_called()
    mock_logger_error.assert_called_with("Invalid email address provided: invalid-email")


# ** Run All Tests with: **
# pytest test_debugger_reporter.py