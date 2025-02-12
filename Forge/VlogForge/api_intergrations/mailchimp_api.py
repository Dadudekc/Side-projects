import os
from mailchimp_marketing import Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY")
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID")

# Initialize Mailchimp client
client = Client()
client.set_config({
    "api_key": MAILCHIMP_API_KEY,
    "server": "usX"  # Replace with your server prefix (e.g., 'us19')
})

def add_subscriber(email):
    """
    Add a subscriber to the Mailchimp list.
    
    :param email: The email address of the subscriber.
    """
    try:
        response = client.lists.add_list_member(MAILCHIMP_LIST_ID, {
            "email_address": email,
            "status": "subscribed"
        })
        return response
    except Exception as e:
        return {"error": f"Failed to add subscriber: {str(e)}"}

def send_campaign(subject, body):
    """
    Send an email campaign to the Mailchimp list.
    
    :param subject: The subject of the email.
    :param body: The body of the email (HTML content).
    """
    try:
        # Create a campaign
        campaign = client.campaigns.create({
            "type": "regular",
            "recipients": {
                "list_id": MAILCHIMP_LIST_ID
            },
            "settings": {
                "subject_line": subject,
                "title": subject,
                "from_name": "Your Name",
                "reply_to": "your_email@example.com"
            }
        })
        
        # Set the body content (HTML)
        client.campaigns.set_content(campaign["id"], {"html": body})
        
        # Send the campaign
        client.campaigns.send(campaign["id"])
        
        return {"status": "Campaign sent successfully."}
    except Exception as e:
        return {"error": f"Failed to send campaign: {str(e)}"}

# Example usage
if __name__ == "__main__":
    # Adding a subscriber
    add_subscriber("test@example.com")
    
    # Sending a campaign
    send_campaign("Test Subject", "<h1>This is a test email</h1>")
