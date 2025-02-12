import csv
from datetime import datetime, timedelta

class ContentManager:
    def __init__(self, schedule_file='data/content_schedule.csv'):
        self.schedule_file = schedule_file
        self.content_schedule = self.load_schedule()

    def load_schedule(self):
        try:
            with open(self.schedule_file, mode='r') as file:
                reader = csv.DictReader(file)
                return [row for row in reader]
        except FileNotFoundError:
            return []

    def save_schedule(self):
        with open(self.schedule_file, mode='w', newline='') as file:
            fieldnames = ['Date', 'Title', 'Status']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.content_schedule)

    def add_content(self, date, title, status='Draft'):
        # Date validation
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        new_content = {'Date': date, 'Title': title, 'Status': status}
        self.content_schedule.append(new_content)
        self.save_schedule()

    def update_status(self, title, new_status):
        for content in self.content_schedule:
            if content['Title'] == title:
                content['Status'] = new_status
                break
        self.save_schedule()

    def auto_update_status(self):
        today = datetime.now().date()
        for content in self.content_schedule:
            post_date = datetime.strptime(content['Date'], '%Y-%m-%d').date()
            if content['Status'] == 'Scheduled' and post_date <= today:
                content['Status'] = 'Posted'
        self.save_schedule()

    def get_upcoming_content(self):
        today = datetime.now().date()
        return [content for content in self.content_schedule if datetime.strptime(content['Date'], '%Y-%m-%d').date() > today]

    def get_due_reminders(self, remind_before=0):
        today = datetime.now().date()
        reminder_date = today + timedelta(days=remind_before)

        return [
            content for content in self.content_schedule
            if datetime.strptime(content['Date'], '%Y-%m-%d').date() == reminder_date
               and content['Status'] == 'Scheduled'
        ]

    def suggest_optimal_posting_time(self, engagement_data):
        if not engagement_data:
            return None

        # Group engagement by time and calculate average
        avg_engagement = {}
        for entry in engagement_data:
            time = entry['Time']
            avg_engagement.setdefault(time, []).append(entry['Engagement'])

        # Determine optimal time based on highest average engagement
        optimal_time = max(
            avg_engagement,
            key=lambda time: sum(avg_engagement[time]) / len(avg_engagement[time])
        )
        return optimal_time

    def schedule_content(self, content_list):
        """
        Schedule multiple content items at once.

        :param content_list: List of content scripts or titles to be scheduled.
        """
        today = datetime.now().strftime('%Y-%m-%d')
        for item in content_list:
            self.add_content(date=today, title=item[:30], status='Scheduled')
