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
@patch.object(EmailReporter, "send_report", return_value=True)
def test_send_email_report(mock_send_report, reporter):
    """Test sending an email report with a valid email."""
    email_reporter = EmailReporter()
    email_reporter.sender_email = "test@example.com"
    email_reporter.sender_password = "password123"
    email_reporter.recipient_email = "recipient@example.com"

    reporter.email_reporter = email_reporter
    
    reporter.send_email_report(email_reporter.recipient_email)

    mock_send_report.assert_called_once()

@patch("ai_engine.models.debugger.debugger_reporter.logger.error")
@patch.object(EmailReporter, "send_report")
def test_send_email_invalid_email(mock_send_email, mock_logger_error, reporter):
    """Test that an invalid email prevents sending a report and logs an error."""
    reporter.send_email_report("invalid-email")

    mock_send_email.assert_not_called()
    mock_logger_error.assert_called_with("❌ Invalid email address. Skipping report send.")

# ** Run All Tests with: **
# pytest tests/test_debugger_reporter.py
