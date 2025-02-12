import csv
import os
from datetime import datetime, timedelta
import pandas as pd

# ================================
# Setup: Define file path and ensure directory exists
# ================================
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)
REFERRAL_DATA_FILE = os.path.join(DATA_DIR, "referral_data.csv")

# Ensure referral_data.csv exists with headers if it's not present or empty
if not os.path.exists(REFERRAL_DATA_FILE) or os.path.getsize(REFERRAL_DATA_FILE) == 0:
    with open(REFERRAL_DATA_FILE, mode='w', newline='') as file:
        fieldnames = ['referral_id', 'referring_user', 'referred_user', 'referral_status', 'referral_date', 'incentive_awarded']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

# ================================
# Helper Functions for CSV Read/Write
# ================================
def read_referral_data():
    with open(REFERRAL_DATA_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def write_referral_data(referral_data):
    with open(REFERRAL_DATA_FILE, mode='w', newline='') as file:
        fieldnames = ['referral_id', 'referring_user', 'referred_user', 'referral_status', 'referral_date', 'incentive_awarded']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(referral_data)

# ================================
# Basic Referral Management Functions
# ================================
def add_referral(referring_user, referred_user, incentive_awarded=0):
    referral_data = read_referral_data()
    referral_id = len(referral_data) + 1
    referral_status = 'active'
    referral_date = datetime.now().strftime('%Y-%m-%d')
    new_referral = {
        'referral_id': referral_id,
        'referring_user': referring_user,
        'referred_user': referred_user,
        'referral_status': referral_status,
        'referral_date': referral_date,
        'incentive_awarded': incentive_awarded
    }
    # Append new referral to CSV
    with open(REFERRAL_DATA_FILE, mode='a', newline='') as file:
        fieldnames = ['referral_id', 'referring_user', 'referred_user', 'referral_status', 'referral_date', 'incentive_awarded']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Write header if file is empty
        if os.path.getsize(REFERRAL_DATA_FILE) == 0:
            writer.writeheader()
        writer.writerow(new_referral)
    return new_referral

def update_referral_status(referral_id, new_status):
    referral_data = read_referral_data()
    for referral in referral_data:
        if int(referral['referral_id']) == referral_id:
            referral['referral_status'] = new_status
            break
    write_referral_data(referral_data)

def assign_incentive(referral_id, incentive_amount):
    referral_data = read_referral_data()
    for referral in referral_data:
        if int(referral['referral_id']) == referral_id:
            referral['incentive_awarded'] = incentive_amount
            break
    write_referral_data(referral_data)

def generate_referral_report():
    referral_data = read_referral_data()
    report = {
        'total_referrals': len(referral_data),
        'active_referrals': sum(1 for r in referral_data if r['referral_status'] == 'active'),
        'completed_referrals': sum(1 for r in referral_data if r['referral_status'] == 'completed'),
        'total_incentives_awarded': sum(float(r['incentive_awarded']) for r in referral_data)
    }
    return report

# ================================
# Bonus System & Notification Enhancements
# ================================
# Define bonus thresholds: e.g., 3 completed → $15, 5 completed → $30, 10 completed → $50
BONUS_THRESHOLDS = {3: 15, 5: 30, 10: 50}

def apply_custom_bonus():
    referral_data = read_referral_data()
    # Count completed referrals per user
    referral_counts = {}
    for referral in referral_data:
        if referral['referral_status'] == 'completed':
            user = referral['referring_user']
            referral_counts[user] = referral_counts.get(user, 0) + 1
    # Calculate total bonus per user based on thresholds
    bonuses_applied = {}
    for user, count in referral_counts.items():
        total_bonus = sum(bonus for threshold, bonus in BONUS_THRESHOLDS.items() if count >= threshold)
        bonuses_applied[user] = total_bonus
    return bonuses_applied

def automate_bonus_assignment():
    referral_data = read_referral_data()
    bonuses_awarded = apply_custom_bonus()
    # Update each referral's incentive (for completed referrals) to the bonus total for that user
    for referral in referral_data:
        user = referral['referring_user']
        if referral['referral_status'] == 'completed' and user in bonuses_awarded:
            referral['incentive_awarded'] = bonuses_awarded[user]
    write_referral_data(referral_data)

def revoke_expired_bonuses():
    referral_data = read_referral_data()
    # For each referral that is expired, revoke any assigned bonus
    for referral in referral_data:
        if referral['referral_status'] == 'expired':
            referral['incentive_awarded'] = 0
    write_referral_data(referral_data)

def generate_date_range_report(start_date, end_date):
    referral_data = read_referral_data()
    report = {}
    # Filter referrals within the provided date range
    filtered_data = [
        r for r in referral_data
        if start_date <= datetime.strptime(r['referral_date'], '%Y-%m-%d') <= end_date
    ]
    # Group report by referring user
    for referral in filtered_data:
        key = referral['referring_user']
        if key not in report:
            report[key] = {
                'total_referrals': 0,
                'completed_referrals': 0,
                'active_referrals': 0,
                'expired_referrals': 0,
                'total_incentives_awarded': 0
            }
        report[key]['total_referrals'] += 1
        report[key]['total_incentives_awarded'] += float(referral['incentive_awarded'])
        if referral['referral_status'] == 'completed':
            report[key]['completed_referrals'] += 1
        elif referral['referral_status'] == 'active':
            report[key]['active_referrals'] += 1
        elif referral['referral_status'] == 'expired':
            report[key]['expired_referrals'] += 1
    return report

def trigger_notifications_with_custom_expiry(expiry_days=5):
    """
    Trigger notifications:
      - If an active referral is older than expiry_days, notify that it is about to expire.
      - Notify bonus milestones (ensuring each milestone is notified only once per user).
    """
    referral_data = read_referral_data()
    today = datetime.now()
    notifications = []
    milestone_awarded = {}
    # Count completed referrals per user
    bonus_counts = {}
    for referral in referral_data:
        if referral['referral_status'] == 'completed':
            user = referral['referring_user']
            bonus_counts[user] = bonus_counts.get(user, 0) + 1
    for referral in referral_data:
        referral_date = datetime.strptime(referral['referral_date'], '%Y-%m-%d')
        days_active = (today - referral_date).days
        if referral['referral_status'] == 'active' and days_active >= expiry_days:
            notifications.append(f"Referral ID {referral['referral_id']} is about to expire for user {referral['referring_user']}.")
        user = referral['referring_user']
        completed_referrals = bonus_counts.get(user, 0)
        for threshold in BONUS_THRESHOLDS:
            if completed_referrals >= threshold and (user, threshold) not in milestone_awarded:
                notifications.append(f"User {user} has reached {threshold} completed referrals and earned a bonus!")
                milestone_awarded[(user, threshold)] = True
    return notifications

# Placeholder function to simulate email notifications
def send_email_notification(subject, message, recipient):
    # For a real implementation, integrate with an email service (e.g., SMTP, SendGrid, etc.)
    print(f"Sending email to {recipient}:\nSubject: {subject}\nMessage: {message}\n")

# ================================
# Testing Code: Adding Test Data & Simulating Features
# ================================
if __name__ == "__main__":
    # (Optional) Clear existing data for testing; comment out in production.
    # with open(REFERRAL_DATA_FILE, mode='w', newline='') as file:
    #     fieldnames = ['referral_id', 'referring_user', 'referred_user', 'referral_status', 'referral_date', 'incentive_awarded']
    #     writer = csv.DictWriter(file, fieldnames=fieldnames)
    #     writer.writeheader()

    # Add a new referral and update its status as an example
    add_referral('user123', 'user456', incentive_awarded=10)
    update_referral_status(1, 'completed')
    assign_incentive(1, 15)
    
    # Test: Add a referral that is older than the expiry threshold (set to 5 days for testing)
    test_referral = {
        "referral_id": len(read_referral_data()) + 1,
        "referring_user": "investor_006",
        "referred_user": "new_user_106",
        "referral_status": "active",
        "referral_date": (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'),
        "incentive_awarded": 0
    }
    data = read_referral_data()
    data.append(test_referral)
    write_referral_data(data)

    # Test: Add additional referrals for investor_001 to simulate reaching 10 completed referrals
    additional_referrals_for_10 = [
        {"referral_id": len(read_referral_data()) + i + 1, 
         "referring_user": "investor_001", 
         "referred_user": f"new_user_{110+i}", 
         "referral_status": "completed", 
         "referral_date": (datetime.now() - timedelta(days=4-i)).strftime('%Y-%m-%d'), 
         "incentive_awarded": 15}
        for i in range(5)
    ]
    data = read_referral_data()
    data.extend(additional_referrals_for_10)
    write_referral_data(data)

    # Apply automated bonus assignment and revoke bonuses for expired referrals
    automate_bonus_assignment()
    revoke_expired_bonuses()

    # Trigger notifications with a custom expiry threshold (set to 5 days for testing)
    final_notifications = trigger_notifications_with_custom_expiry(expiry_days=5)
    
    # Generate a detailed date range report for the last 30 days
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    detailed_report = generate_date_range_report(start_date, end_date)
    report_df = pd.DataFrame.from_dict(detailed_report, orient='index')
    
    # Display final notifications
    print("Final Notifications:")
    for note in final_notifications:
        print(note)
    
    # Display the detailed referral report
    print("\nMonthly Referral Report:")
    print(report_df)
    
    # Simulate sending email notifications for each notification
    for note in final_notifications:
        send_email_notification("Referral Notification", note, "user@example.com")
