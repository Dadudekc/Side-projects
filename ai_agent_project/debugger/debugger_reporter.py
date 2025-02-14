import logging
import json
from typing import Dict
from email_reporter import EmailReporter  # Optional email notifications

logger = logging.getLogger("DebuggerReporter")
logger.setLevel(logging.DEBUG)

REPORT_FILE = "debugging_report.json"

class DebuggerReporter:
    """
    Generates debugging session reports with AI analysis.
    """

    def __init__(self):
        self.report_data = {"failed_patches": {}, "ai_explanations": {}}

    def log_failed_patch(self, error_signature: str, reason: str):
        """Logs failed patch explanations."""
        self.report_data["failed_patches"][error_signature] = reason

    def save_report(self):
        """Saves debugging report to JSON."""
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.report_data, f, indent=4)
        logger.info(f"📄 Debugging report saved: {REPORT_FILE}")

    def send_email_report(self):
        """Optional: Sends debugging summary via email."""
        email_client = EmailReporter()
        email_client.send_debugging_report(self.report_data)
