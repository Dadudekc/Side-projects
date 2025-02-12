import os
from mailchimp_marketing import Client
from dotenv import load_dotenv

class MailchimpManager:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_key = os.getenv("MAILCHIMP_API_KEY")
        self.list_id = os.getenv("MAILCHIMP_LIST_ID")
        self.server_prefix = os.getenv("MAILCHIMP_SERVER", "usX")  # Default to 'usX' if not set

        # Initialize Mailchimp client
        self.client = Client()
        self.client.set_config({
            "api_key": self.api_key,
            "server": self.server_prefix
        })

    def add_subscriber(self, email):
        """
        Add a subscriber to the Mailchimp list.

        :param email: The email address of the subscriber.
        """
        try:
            response = self.client.lists.add_list_member(self.list_id, {
                "email_address": email,
                "status": "subscribed"
            })
            return response
        except Exception as e:
            return {"error": f"Failed to add subscriber: {str(e)}"}

    def send_campaign(self, subject, body):
        """
        Send an email campaign to the Mailchimp list.

        :param subject: The subject of the email.
        :param body: The body of the email (HTML content).
        """
        try:
            # Create a campaign
            campaign = self.client.campaigns.create({
                "type": "regular",
                "recipients": {
                    "list_id": self.list_id
                },
                "settings": {
                    "subject_line": subject,
                    "title": subject,
                    "from_name": "Your Name",
                    "reply_to": "your_email@example.com"
                }
            })

            # Set the body content (HTML)
            self.client.campaigns.set_content(campaign["id"], {"html": body})

            # Send the campaign
            self.client.campaigns.send(campaign["id"])

            return {"status": "Campaign sent successfully."}
        except Exception as e:
            return {"error": f"Failed to send campaign: {str(e)}"}

# Example usage
if __name__ == "__main__":
    mailchimp_manager = MailchimpManager()
    
    # Adding a subscriber
    print(mailchimp_manager.add_subscriber("test@example.com"))

    # Sending a campaign
    print(mailchimp_manager.send_campaign("Test Subject", "<h1>This is a test email</h1>"))
