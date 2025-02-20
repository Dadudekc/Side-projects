"""
This module provides a class `DebuggerReporter` which generates detailed debugging session reports 
with AI analysis and logs failed patches and AI explanations. The report is stored locally in a JSON 
file and can be sent via email to a recipient.

Class Methods:
    - __init__: Initializes a new instance of the class and loads any existing report if available.
    - load_existing_report: Loads the existing debugging report or initializes a new one.
    - log_failed_patch: Logs a failed patch attempt with a reason.
    - log_ai_explanation: Logs AI-generated debugging insights.
    - save_report: Saves debugging session data to a JSON file.
    - send_email_report: Sends the debugging report via email with validation.
"""

import logging
import json
import os
from typing import Dict
from ai_engine.models.debugger.email_reporter import EmailReporter

logger = logging.getLogger("DebuggerReporter")
logger.setLevel(logging.DEBUG)

REPORT_FILE = "debugging_report.json"

class DebuggerReporter:
    """
    Generates detailed debugging session reports with AI analysis.
    - Logs failed patches and AI explanations.
    - Saves and merges reports for debugging history tracking.
    - Optionally sends an email summary.
    """

    def __init__(self):
        self.report_data = self.load_existing_report()
        self.email_reporter = None  # Initialize email reporter only when needed

    def load_existing_report(self) -> Dict[str, Dict[str, str]]:
        """Loads the existing debugging report or initializes a new one."""
        if os.path.exists(REPORT_FILE):
            try:
                with open(REPORT_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"❌ Corrupted JSON in {REPORT_FILE}. Resetting report.")
            except Exception as e:
                logger.error(f"❌ Failed to load existing report: {e}")
        
        return {"failed_patches": {}, "ai_explanations": {}}

    def log_failed_patch(self, error_signature: str, reason: str):
        """
        Logs a failed patch attempt with a reason.

        Args:
            error_signature (str): Unique hash of the error.
            reason (str): Explanation of why the patch failed.
        """
        self.report_data["failed_patches"][error_signature] = reason
        logger.warning(f"❌ Patch failed for {error_signature}: {reason}")

    def log_ai_explanation(self, error_signature: str, explanation: str):
        """
        Logs an AI-generated explanation for debugging insights.

        Args:
            error_signature (str): Unique hash of the error.
            explanation (str): AI analysis or suggestion.
        """
        self.report_data["ai_explanations"][error_signature] = explanation
        logger.info(f"🤖 AI Analysis added for {error_signature}: {explanation}")

    def save_report(self):
        """Saves debugging session data to a JSON file."""
        try:
            with open(REPORT_FILE, "w", encoding="utf-8") as f:
                json.dump(self.report_data, f, indent=4)
            logger.info(f"📄 Debugging report saved ({len(self.report_data['failed_patches'])} failures).")
        except Exception as e:
            logger.error(f"❌ Failed to save report: {e}")

    def send_email_report(self, recipient_email: str):
        """
        Sends the debugging report via email.

        Args:
            recipient_email (str): Email address of the recipient.
        """
        if not recipient_email or "@" not in recipient_email:
            logger.error("❌ Invalid email address. Skipping report send.")
            return

        # Ensure email credentials are available
        if not self.email_reporter:
            self.email_reporter = EmailReporter()

        if not self.email_reporter.sender_email or not self.email_reporter.sender_password:
            logger.error("❌ Missing email credentials. Cannot send report.")
            return

        logger.info(f"📧 Sending debugging report to {recipient_email}...")

        try:
            success = self.email_reporter.send_report(self.report_data, recipient_email)
            if success:
                logger.info(f"✅ Debugging report sent successfully to {recipient_email}.")
            else:
                logger.error(f"❌ Failed to send debugging report to {recipient_email}.")
        except Exception as e:
            logger.error(f"❌ Error sending email report: {e}")

# Example Usage:
if __name__ == "__main__":
    reporter = DebuggerReporter()
    reporter.log_failed_patch("hash1234", "Patch introduced syntax error.")
    reporter.log_ai_explanation("hash1234", "Consider adding a missing import.")
    reporter.save_report()
    reporter.send_email_report("debugger@example.com")
