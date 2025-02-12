import csv
import os
import logging
from datetime import datetime, timedelta
import pandas as pd

# Configure logging to display info and error messages.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ReferralManager:
    # Define the expected CSV fieldnames and bonus thresholds.
    FIELDNAMES = ['referral_id', 'referring_user', 'referred_user', 'referral_status', 'referral_date', 'incentive_awarded']
    BONUS_THRESHOLDS = {3: 15, 5: 30, 10: 50}

    def __init__(self, data_dir=None, filename="referral_data.csv"):
        """
        Initialize the ReferralManager.
        - Creates the data directory if needed.
        - Ensures that the CSV file exists and is in a valid state.
        """
        self.data_dir = data_dir if data_dir else os.path.join(os.getcwd(), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.referral_data_file = os.path.join(self.data_dir, filename)
        self._ensure_file()

    def _ensure_file(self):
        """
        Ensure that the CSV file exists and is not empty.
        If the file is missing or empty, “heal” it by writing the header.
        """
        if not os.path.exists(self.referral_data_file) or os.path.getsize(self.referral_data_file) == 0:
            self._heal_csv_file()

    def _heal_csv_file(self):
        """
        Self-healing method that (re)creates the CSV file with the correct header.
        """
        try:
            with open(self.referral_data_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
                writer.writeheader()
            logging.info("CSV file healed and initialized.")
        except Exception as e:
            logging.error("Failed to heal CSV file: " + str(e))

    def _read_referral_data(self):
        """
        Reads and returns the referral data from the CSV file.
        If the file is corrupt or the header is not as expected, the CSV is healed.
        """
        try:
            with open(self.referral_data_file, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                if reader.fieldnames != self.FIELDNAMES:
                    raise ValueError("CSV header mismatch; healing file.")
                data = list(reader)
            return data
        except Exception as e:
            logging.error("Error reading CSV file: " + str(e))
            self._heal_csv_file()
            return []

    def _write_referral_data(self, data):
        """
        Writes the provided referral data to the CSV file.
        """
        try:
            with open(self.referral_data_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            logging.error("Error writing CSV file: " + str(e))
            self._heal_csv_file()

    def add_referral(self, referring_user, referred_user, incentive_awarded=0):
        """
        Adds a new referral to the CSV file.
        Returns the new referral record (or None if an error occurred).
        """
        data = self._read_referral_data()
        try:
            referral_id = len(data) + 1
            referral_date = datetime.now().strftime('%Y-%m-%d')
            new_referral = {
                'referral_id': referral_id,
                'referring_user': referring_user,
                'referred_user': referred_user,
                'referral_status': 'active',
                'referral_date': referral_date,
                'incentive_awarded': incentive_awarded
            }
            # Append new referral in append mode
            with open(self.referral_data_file, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.FIELDNAMES)
                # If the file is empty (or just healed), write the header.
                if os.path.getsize(self.referral_data_file) == 0:
                    writer.writeheader()
                writer.writerow(new_referral)
            logging.info(f"Added referral: {new_referral}")
            return new_referral
        except Exception as e:
            logging.error("Error adding referral: " + str(e))
            self._heal_csv_file()
            return None

    def update_referral_status(self, referral_id, new_status):
        """
        Updates the status of a referral given its ID.
        """
        data = self._read_referral_data()
        updated = False
        for referral in data:
            try:
                if int(referral['referral_id']) == referral_id:
                    referral['referral_status'] = new_status
                    updated = True
                    break
            except Exception as e:
                logging.error("Error updating referral status: " + str(e))
        if updated:
            self._write_referral_data(data)
            logging.info(f"Referral ID {referral_id} status updated to '{new_status}'.")
        else:
            logging.warning(f"Referral ID {referral_id} not found.")

    def assign_incentive(self, referral_id, incentive_amount):
        """
        Assigns an incentive to a referral given its ID.
        """
        data = self._read_referral_data()
        updated = False
        for referral in data:
            try:
                if int(referral['referral_id']) == referral_id:
                    referral['incentive_awarded'] = incentive_amount
                    updated = True
                    break
            except Exception as e:
                logging.error("Error assigning incentive: " + str(e))
        if updated:
            self._write_referral_data(data)
            logging.info(f"Incentive for referral ID {referral_id} set to {incentive_amount}.")
        else:
            logging.warning(f"Referral ID {referral_id} not found.")

    def generate_referral_report(self):
        """
        Generates a summary report of all referrals.
        """
        data = self._read_referral_data()
        report = {
            'total_referrals': len(data),
            'active_referrals': sum(1 for r in data if r.get('referral_status') == 'active'),
            'completed_referrals': sum(1 for r in data if r.get('referral_status') == 'completed'),
            'total_incentives_awarded': sum(float(r.get('incentive_awarded', 0)) for r in data)
        }
        return report

    def apply_custom_bonus(self):
        """
        Calculates bonus amounts based on the number of completed referrals per user.
        Returns a dictionary mapping users to bonus amounts.
        """
        data = self._read_referral_data()
        referral_counts = {}
        for referral in data:
            if referral.get('referral_status') == 'completed':
                user = referral.get('referring_user')
                referral_counts[user] = referral_counts.get(user, 0) + 1
        bonuses_applied = {}
        for user, count in referral_counts.items():
            total_bonus = sum(bonus for threshold, bonus in self.BONUS_THRESHOLDS.items() if count >= threshold)
            bonuses_applied[user] = total_bonus
        return bonuses_applied

    def automate_bonus_assignment(self):
        """
        Automatically assigns the bonus incentive to completed referrals.
        """
        data = self._read_referral_data()
        bonuses_awarded = self.apply_custom_bonus()
        for referral in data:
            user = referral.get('referring_user')
            if referral.get('referral_status') == 'completed' and user in bonuses_awarded:
                referral['incentive_awarded'] = bonuses_awarded[user]
        self._write_referral_data(data)
        logging.info("Automated bonus assignment completed.")

    def revoke_expired_bonuses(self):
        """
        Revokes (resets) bonus incentives for referrals marked as expired.
        """
        data = self._read_referral_data()
        for referral in data:
            if referral.get('referral_status') == 'expired':
                referral['incentive_awarded'] = 0
        self._write_referral_data(data)
        logging.info("Expired bonuses revoked.")

    def generate_date_range_report(self, start_date, end_date):
        """
        Generates a detailed report for referrals within a given date range.
        Returns a dictionary grouped by the referring user.
        """
        data = self._read_referral_data()
        report = {}
        filtered_data = []
        for r in data:
            try:
                r_date = datetime.strptime(r.get('referral_date'), '%Y-%m-%d')
                if start_date <= r_date <= end_date:
                    filtered_data.append(r)
            except Exception as e:
                logging.error("Error parsing date for referral: " + str(e))
        for referral in filtered_data:
            user = referral.get('referring_user')
            if user not in report:
                report[user] = {
                    'total_referrals': 0,
                    'completed_referrals': 0,
                    'active_referrals': 0,
                    'expired_referrals': 0,
                    'total_incentives_awarded': 0
                }
            report[user]['total_referrals'] += 1
            try:
                report[user]['total_incentives_awarded'] += float(referral.get('incentive_awarded', 0))
            except Exception as e:
                logging.error("Error converting incentive_awarded: " + str(e))
            status = referral.get('referral_status')
            if status == 'completed':
                report[user]['completed_referrals'] += 1
            elif status == 'active':
                report[user]['active_referrals'] += 1
            elif status == 'expired':
                report[user]['expired_referrals'] += 1
        return report

    def trigger_notifications_with_custom_expiry(self, expiry_days=5):
        """
        Triggers notifications based on the following rules:
          - If an active referral is older than expiry_days, notify that it is about to expire.
          - Notify bonus milestones (each milestone notification is sent only once per user).
        Returns a list of notification messages.
        """
        data = self._read_referral_data()
        today = datetime.now()
        notifications = []
        milestone_awarded = {}
        bonus_counts = {}

        # Count completed referrals per user for bonus milestones.
        for referral in data:
            if referral.get('referral_status') == 'completed':
                user = referral.get('referring_user')
                bonus_counts[user] = bonus_counts.get(user, 0) + 1

        for referral in data:
            try:
                referral_date = datetime.strptime(referral.get('referral_date'), '%Y-%m-%d')
            except Exception as e:
                logging.error("Error parsing referral_date: " + str(e))
                continue

            days_active = (today - referral_date).days
            if referral.get('referral_status') == 'active' and days_active >= expiry_days:
                notifications.append(
                    f"Referral ID {referral.get('referral_id')} is about to expire for user {referral.get('referring_user')}."
                )
            user = referral.get('referring_user')
            completed_referrals = bonus_counts.get(user, 0)
            for threshold in self.BONUS_THRESHOLDS:
                if completed_referrals >= threshold and (user, threshold) not in milestone_awarded:
                    notifications.append(
                        f"User {user} has reached {threshold} completed referrals and earned a bonus!"
                    )
                    milestone_awarded[(user, threshold)] = True
        return notifications

    @staticmethod
    def send_email_notification(subject, message, recipient):
        """
        Placeholder for sending an email notification.
        In a production system, integrate with an SMTP server or an email API.
        """
        print(f"Sending email to {recipient}:\nSubject: {subject}\nMessage: {message}\n")


# ================================
# Testing Code: Adding Test Data & Simulating Features
# ================================
if __name__ == "__main__":
    # Instantiate the manager.
    manager = ReferralManager()

    # (Optional) For testing purposes, you may want to clear existing data.
    # Uncomment the following line to reinitialize the CSV file.
    # manager._heal_csv_file()

    # Add a new referral and then update its status and incentive.
    manager.add_referral('user123', 'user456', incentive_awarded=10)
    manager.update_referral_status(1, 'completed')
    manager.assign_incentive(1, 15)

    # Test: Add a referral that is older than the expiry threshold (set to 5 days for testing).
    test_referral = {
        "referral_id": len(manager._read_referral_data()) + 1,
        "referring_user": "investor_006",
        "referred_user": "new_user_106",
        "referral_status": "active",
        "referral_date": (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
        "incentive_awarded": 0
    }
    data = manager._read_referral_data()
    data.append(test_referral)
    manager._write_referral_data(data)

    # Test: Add additional referrals for investor_001 to simulate reaching bonus milestones.
    additional_referrals_for_10 = [
        {
            "referral_id": len(manager._read_referral_data()) + i + 1,
            "referring_user": "investor_001",
            "referred_user": f"new_user_{110 + i}",
            "referral_status": "completed",
            "referral_date": (datetime.now() - timedelta(days=4 - i)).strftime('%Y-%m-%d'),
            "incentive_awarded": 15
        }
        for i in range(5)
    ]
    data = manager._read_referral_data()
    data.extend(additional_referrals_for_10)
    manager._write_referral_data(data)

    # Apply automated bonus assignment and revoke bonuses for expired referrals.
    manager.automate_bonus_assignment()
    manager.revoke_expired_bonuses()

    # Trigger notifications with a custom expiry threshold (5 days for testing).
    notifications = manager.trigger_notifications_with_custom_expiry(expiry_days=5)
    print("Final Notifications:")
    for note in notifications:
        print(note)

    # Generate a detailed referral report for the last 30 days.
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    detailed_report = manager.generate_date_range_report(start_date, end_date)
    report_df = pd.DataFrame.from_dict(detailed_report, orient='index')

    print("\nMonthly Referral Report:")
    print(report_df)

    # Simulate sending email notifications for each notification.
    for note in notifications:
        ReferralManager.send_email_notification("Referral Notification", note, "user@example.com")
