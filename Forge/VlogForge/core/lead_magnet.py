import re
import time
from datetime import datetime, timedelta
import requests
import unittest
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
MAILCHIMP_API_KEY = os.getenv('MAILCHIMP_API_KEY')
MAILCHIMP_API_ENDPOINT = os.getenv('MAILCHIMP_API_ENDPOINT')

# Check if environment variables are set correctly
if not MAILCHIMP_API_KEY or not MAILCHIMP_API_ENDPOINT:
    raise ValueError("Mailchimp API key or endpoint not set. Please check your .env file.")

class LeadMagnet:
    def __init__(self):
        self.leads = {}
        self.follow_up_days = 3  # Default follow-up days

    def is_valid_email(self, email):
        return re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)

    def send_resource(self, email):
        if not email:
            return {"success": False, "message": "Email address is required."}

        if not self.is_valid_email(email):
            return {"success": False, "message": "Invalid email address."}

        if email in self.leads and self.leads[email]['status'] != 'new':
            return {"success": False, "message": "Resource already sent to this email."}

        self.leads[email] = {
            "email": email,
            "status": "resource_sent",
            "last_contacted": datetime.now(),
            "lead_score": 0  # Initialize lead score
        }
        self.send_email(email, "Here's your free resource!")
        return {"success": True, "message": "Resource sent successfully."}

    def track_conversion(self, email):
        if email in self.leads:
            self.leads[email]['status'] = 'converted'
            self.leads[email]['lead_score'] += 10  # Increase lead score on conversion
        else:
            self.leads[email] = {"email": email, "status": "converted", "lead_score": 10}

    def get_lead(self, email):
        return self.leads.get(email, None)

    def send_follow_up_emails(self):
        for email, lead in self.leads.items():
            follow_up_days = lead.get('follow_up_days', self.follow_up_days)  # Custom interval support
            if (lead['status'] == 'resource_sent' and
                datetime.now() - lead['last_contacted'] > timedelta(days=follow_up_days)):
                self.send_email(email, "Following up: Did you find the resource helpful?")
                self.leads[email]['last_contacted'] = datetime.now()
                self.leads[email]['lead_score'] += 1  # Increase lead score on follow-up

    def send_email(self, email, content):
        try:
            response = requests.post(
                MAILCHIMP_API_ENDPOINT,
                auth=("anystring", MAILCHIMP_API_KEY),
                json={"email": email, "message": content}
            )
            if response.status_code == 200:
                print(f"Email sent to {email}: {content}")
                return True
            else:
                print(f"Failed to send email to {email}: {response.text}")
                return False
        except Exception as e:
            print(f"Error sending email to {email}: {e}")
            return False

# Unit Test for LeadMagnet
class TestLeadMagnet(unittest.TestCase):
    def setUp(self):
        self.lead_magnet = LeadMagnet()
        self.mock_leads = [
            {"email": "user1@example.com", "status": "new"},
            {"email": "user2@example.com", "status": "new"},
        ]

    def test_send_resource_success(self):
        response = self.lead_magnet.send_resource(self.mock_leads[0]["email"])
        self.assertTrue(response["success"])
        self.assertEqual(response["message"], "Resource sent successfully.")

    def test_send_resource_invalid_email(self):
        response = self.lead_magnet.send_resource("invalid-email")
        self.assertFalse(response["success"])
        self.assertEqual(response["message"], "Invalid email address.")

    def test_track_conversion(self):
        self.lead_magnet.track_conversion(self.mock_leads[0]["email"])
        lead = self.lead_magnet.get_lead(self.mock_leads[0]["email"])
        self.assertEqual(lead["status"], "converted")
        self.assertEqual(lead["lead_score"], 10)

    def test_prevent_duplicate_emails(self):
        self.lead_magnet.send_resource(self.mock_leads[0]["email"])
        response = self.lead_magnet.send_resource(self.mock_leads[0]["email"])
        self.assertFalse(response["success"])
        self.assertEqual(response["message"], "Resource already sent to this email.")

    def test_handle_missing_data(self):
        response = self.lead_magnet.send_resource("")
        self.assertFalse(response["success"])
        self.assertEqual(response["message"], "Email address is required.")

    def test_send_follow_up_emails(self):
        self.lead_magnet.send_resource(self.mock_leads[0]["email"])
        self.lead_magnet.leads[self.mock_leads[0]["email"]]['last_contacted'] -= timedelta(days=4)

        self.lead_magnet.send_follow_up_emails()
        lead = self.lead_magnet.get_lead(self.mock_leads[0]["email"])
        self.assertTrue(lead['last_contacted'] > datetime.now() - timedelta(days=1))
        self.assertEqual(lead['lead_score'], 1)

if __name__ == '__main__':
    unittest.main()
