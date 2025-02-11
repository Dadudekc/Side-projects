import re

class LeadMagnet:
    def __init__(self):
        self.leads = {}

    def is_valid_email(self, email):
        # Simple regex for email validation
        return re.match(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)

    def send_resource(self, email):
        if not email:
            return {"success": False, "message": "Email address is required."}

        if not self.is_valid_email(email):
            return {"success": False, "message": "Invalid email address."}

        if email in self.leads and self.leads[email]['status'] != 'new':
            return {"success": False, "message": "Resource already sent to this email."}

        # Simulate sending resource
        self.leads[email] = {"email": email, "status": "resource_sent"}
        return {"success": True, "message": "Resource sent successfully."}

    def track_conversion(self, email):
        if email in self.leads:
            self.leads[email]['status'] = 'converted'
        else:
            self.leads[email] = {"email": email, "status": "converted"}

    def get_lead(self, email):
        return self.leads.get(email, None)
