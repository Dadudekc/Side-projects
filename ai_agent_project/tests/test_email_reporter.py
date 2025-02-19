import unittest
from email_reporter import EmailReporter

class TestEmailReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = EmailReporter(
            sender_email="your-email@gmail.com",
            sender_password="your-app-password",
            recipient_email="recipient@example.com"
        )

    def test_email_validation(self):
        self.assertTrue(self.reporter.validate_email("valid.email@example.com"))
        self.assertFalse(self.reporter.validate_email("invalid-email"))

    def test_send_email_failure_missing_credentials(self):
        reporter = EmailReporter("", "", "")
        self.assertFalse(reporter.send_email("Test", "This should fail"))

if __name__ == "__main__":
    unittest.main()
