import unittest
from datetime import datetime, timedelta
from VlogForge.core.content_manager import ContentManager


class TestContentManager(unittest.TestCase):
    def setUp(self):
        # Use an in-memory list instead of an actual file for testing
        self.manager = ContentManager(schedule_file='test_content_schedule.csv')
        self.manager.content_schedule = []  # Clear schedule before each test

    def test_add_and_auto_update_content(self):
        today = datetime.now().strftime('%Y-%m-%d')
        self.manager.add_content(today, 'Auto Update Test', 'Scheduled')
        self.manager.auto_update_status()
        content = self.manager.content_schedule[0]
        self.assertEqual(content['Status'], 'Posted')

    def test_suggest_optimal_time_with_content_addition(self):
        engagement_data = [
            {"Date": "2025-02-01", "Time": "10:00", "Engagement": 50},
            {"Date": "2025-02-02", "Time": "14:00", "Engagement": 120},
            {"Date": "2025-02-03", "Time": "18:00", "Engagement": 90},
            {"Date": "2025-02-04", "Time": "14:00", "Engagement": 150},
        ]
        optimal_time = self.manager.suggest_optimal_posting_time(engagement_data)
        self.manager.add_content('2025-02-15', f'Content at {optimal_time}', 'Draft')
        added_content = self.manager.content_schedule[0]
        self.assertIn(optimal_time, added_content['Title'])

    def test_due_reminders_with_custom_interval(self):
        future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.manager.add_content(future_date, 'Reminder Test', 'Scheduled')
        reminders = self.manager.get_due_reminders(remind_before=1)
        self.assertEqual(len(reminders), 1)
        self.assertEqual(reminders[0]['Title'], 'Reminder Test')

    def test_no_reminders_for_past_content(self):
        past_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        self.manager.add_content(past_date, 'Past Content', 'Scheduled')
        reminders = self.manager.get_due_reminders()
        self.assertEqual(len(reminders), 0)

    def test_upcoming_content(self):
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        self.manager.add_content(future_date, 'Upcoming Content')
        upcoming = self.manager.get_upcoming_content()
        self.assertEqual(len(upcoming), 1)
        self.assertEqual(upcoming[0]['Title'], 'Upcoming Content')

if __name__ == '__main__':
    unittest.main()
