"""
A Python class for sending email notifications for test failures through SMTP.

This class encapsulates the process of creating and sending an email using the SMTP protocol.
A logger called "EmailReporter" is used for error reporting.

Class Attributes:
    smtp_server (str): The SMTP server to connect to. Defaults to "smtp.gmail.com".
    smtp_port (int): The port on which to connect to the SMTP server. Defaults to 587 which is for TLS.
    sender_email (str): The sender's email address.
"""

import smtplib
import logging
import re
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("EmailReporter")


class EmailReporter:
    """Handles sending email notifications for test failures."""

    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587, sender_email=None, sender_password=None, recipient_email=None):
        """
        Initializes EmailReporter with SMTP settings.

        Args:
            smtp_server (str): SMTP server address (default: Gmail SMTP).
            smtp_port (int): SMTP port number (default: 587 for TLS).
            sender_email (str): Sender's email address.
            sender_password (str): Sender's email password or app-specific password.
            recipient_email (str): Recipient's email address.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

    def validate_email(self, email):
        """
        Validates the given email address format.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is valid, False otherwise.
        """
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    def send_email(self, subject, message):
        """
        Sends an email notification.

        Args:
            subject (str): Email subject.
            message (str): Email body content.
        """
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            logger.error("❌ EmailReporter is missing required credentials or recipient email.")
            return False

        if not self.validate_email(self.sender_email):
            logger.error(f"❌ Invalid sender email address: {self.sender_email}")
            return False

        if not self.validate_email(self.recipient_email):
            logger.error(f"❌ Invalid recipient email address: {self.recipient_email}")
            return False

        try:
            # Create email message
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())

            logger.info(f"✅ Email sent successfully to {self.recipient_email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error occurred: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")

        return False  # Indicate failure

    def send_debugging_report(self, subject, debug_info):
        """
        Sends a debugging report via email.

        Args:
            subject (str): Email subject.
            debug_info (str): Debugging details to send.
        """
        formatted_message = f"Debug Report:\n\n{debug_info}"
        return self.send_email(subject, formatted_message)

    def send_report(self, report_data, recipient_email):
        """
        Sends the debugging report via email.

        Args:
            report_data (dict): The debugging report data.
            recipient_email (str): The recipient email address.
        """
        if not self.validate_email(recipient_email):
            logger.error(f"❌ Invalid recipient email address provided: {recipient_email}")
            return False

        self.recipient_email = recipient_email  # Ensure recipient is properly set

        subject = "Debugger Report"
        message = f"Attached is the debugger report:\n\n{json.dumps(report_data, indent=4)}"
        
        return self.send_email(subject, message)
