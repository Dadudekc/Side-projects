import smtplib
import logging
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

    def send_email(self, subject, message):
        """
        Sends an email notification.
        
        Args:
            subject (str): Email subject.
            message (str): Email body content.
        """
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            logger.error("EmailReporter is missing required credentials or recipient email.")
            return

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

            logger.info(f"Email sent successfully to {self.recipient_email}")
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

