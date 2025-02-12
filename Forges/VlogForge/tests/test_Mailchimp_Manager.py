import unittest
from unittest.mock import patch, MagicMock
from VlogForge.api_intergrations.mailchimp_api import MailchimpManager


class TestMailchimpManager(unittest.TestCase):

    @patch('VlogForge.api_intergrations.mailchimp_api.Client')
    def setUp(self, mock_client):
        self.mock_client = mock_client.return_value
        self.mailchimp = MailchimpManager()

    def test_add_subscriber_success(self):
        mock_response = {'id': '12345', 'email_address': 'test@example.com'}
        self.mock_client.lists.add_list_member.return_value = mock_response

        response = self.mailchimp.add_subscriber('test@example.com')
        self.assertEqual(response, mock_response)
        self.mock_client.lists.add_list_member.assert_called_once()

    def test_add_subscriber_failure(self):
        self.mock_client.lists.add_list_member.side_effect = Exception('API error')

        response = self.mailchimp.add_subscriber('test@example.com')
        self.assertIn('error', response)

    def test_send_campaign_success(self):
        self.mock_client.campaigns.create.return_value = {'id': 'campaign123'}
        self.mock_client.campaigns.set_content.return_value = {}
        self.mock_client.campaigns.send.return_value = {}

        response = self.mailchimp.send_campaign('Test Subject', '<h1>Test Body</h1>')
        self.assertEqual(response, {'status': 'Campaign sent successfully.'})
        self.mock_client.campaigns.create.assert_called_once()
        self.mock_client.campaigns.set_content.assert_called_once()
        self.mock_client.campaigns.send.assert_called_once()

    def test_send_campaign_failure(self):
        self.mock_client.campaigns.create.side_effect = Exception('API error')

        response = self.mailchimp.send_campaign('Test Subject', '<h1>Test Body</h1>')
        self.assertIn('error', response)


if __name__ == '__main__':
    unittest.main()
