import unittest
from lead_magnet import LeadMagnet

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

    def test_prevent_duplicate_emails(self):
        self.lead_magnet.send_resource(self.mock_leads[0]["email"])
        response = self.lead_magnet.send_resource(self.mock_leads[0]["email"])
        self.assertFalse(response["success"])
        self.assertEqual(response["message"], "Resource already sent to this email.")

    def test_handle_missing_data(self):
        response = self.lead_magnet.send_resource("")
        self.assertFalse(response["success"])
        self.assertEqual(response["message"], "Email address is required.")

if __name__ == '__main__':
    unittest.main()
