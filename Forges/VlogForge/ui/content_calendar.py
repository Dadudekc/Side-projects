import json
import os
from datetime import datetime, timedelta

class ContentCalendar:
    def __init__(self, storage_path='data/content_calendar.json'):
        self.storage_path = storage_path
        self._ensure_file_exists()
        self.calendar = self._load_calendar()

    def _ensure_file_exists(self):
        # Handle case where storage_path is just a filename without a directory
        directory = os.path.dirname(self.storage_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as file:
                json.dump([], file)  # Initialize with an empty list

    def _load_calendar(self):
        with open(self.storage_path, 'r') as file:
            return json.load(file)

    def _save_calendar(self):
        with open(self.storage_path, 'w') as file:
            json.dump(self.calendar, file, indent=4)

    def add_to_calendar(self, title, scheduled_date, reminder_days=1):
        event = {
            'id': len(self.calendar) + 1,
            'title': title,
            'scheduled_date': scheduled_date,
            'created_at': datetime.now().isoformat(),
            'status': 'Scheduled',
            'reminder_days': reminder_days  # Default to 1-day reminder
        }
        self.calendar.append(event)
        self._save_calendar()
        return event

    def get_scheduled_content(self, date=None, start_date=None, end_date=None):
        if date:
            return [event for event in self.calendar if event['scheduled_date'] == date]
        if start_date and end_date:
            return [event for event in self.calendar if start_date <= event['scheduled_date'] <= end_date]
        return self.calendar

    def update_event(self, event_id, **kwargs):
        for event in self.calendar:
            if event['id'] == event_id:
                event.update(kwargs)
                self._save_calendar()
                return event
        return None

    def delete_event(self, event_id):
        self.calendar = [event for event in self.calendar if event['id'] != event_id]
        self._save_calendar()

    def search_events(self, keyword):
        return [event for event in self.calendar if keyword.lower() in event['title'].lower()]

    def mark_event_completed(self, event_id):
        return self.update_event(event_id, status='Completed')

    def check_missed_events(self):
        today = datetime.now().date()
        for event in self.calendar:
            event_date = datetime.fromisoformat(event['scheduled_date']).date()
            if event['status'] == 'Scheduled' and event_date < today:
                event['status'] = 'Missed'
        self._save_calendar()

    def get_reminders(self):
        today = datetime.now().date()
        reminders = []
        for event in self.calendar:
            reminder_date = datetime.fromisoformat(event['scheduled_date']).date() - timedelta(days=event.get('reminder_days', 1))
            if reminder_date == today:
                reminders.append(event)
        return reminders


# =======================
# Unit Tests for ContentCalendar
# =======================

import unittest

class TestContentCalendar(unittest.TestCase):
    def setUp(self):
        self.calendar = ContentCalendar('test_content_calendar.json')
        self.calendar.calendar = []  # Clear test data
        self.calendar._save_calendar()

    def tearDown(self):
        os.remove('test_content_calendar.json')

    def test_add_to_calendar(self):
        event = self.calendar.add_to_calendar('Test Event', '2024-02-15')
        self.assertEqual(event['title'], 'Test Event')
        self.assertEqual(event['scheduled_date'], '2024-02-15')

    def test_get_scheduled_content(self):
        self.calendar.add_to_calendar('Event 1', '2024-02-15')
        self.calendar.add_to_calendar('Event 2', '2024-02-16')
        events = self.calendar.get_scheduled_content('2024-02-15')
        self.assertEqual(len(events), 1)

    def test_update_event(self):
        event = self.calendar.add_to_calendar('Old Title', '2024-02-15')
        updated_event = self.calendar.update_event(event['id'], title='New Title')
        self.assertEqual(updated_event['title'], 'New Title')

    def test_delete_event(self):
        event = self.calendar.add_to_calendar('To Delete', '2024-02-15')
        self.calendar.delete_event(event['id'])
        events = self.calendar.get_scheduled_content()
        self.assertEqual(len(events), 0)

    def test_search_events(self):
        self.calendar.add_to_calendar('Meeting with Team', '2024-02-15')
        self.calendar.add_to_calendar('Doctor Appointment', '2024-02-16')
        results = self.calendar.search_events('meeting')
        self.assertEqual(len(results), 1)

    def test_mark_event_completed(self):
        event = self.calendar.add_to_calendar('Complete Task', '2024-02-15')
        self.calendar.mark_event_completed(event['id'])
        updated_event = self.calendar.get_scheduled_content('2024-02-15')[0]
        self.assertEqual(updated_event['status'], 'Completed')

    def test_check_missed_events(self):
        past_event = self.calendar.add_to_calendar('Past Event', '2023-01-01')
        self.calendar.check_missed_events()
        updated_event = self.calendar.get_scheduled_content('2023-01-01')[0]
        self.assertEqual(updated_event['status'], 'Missed')

    def test_get_reminders(self):
        today = datetime.now().strftime('%Y-%m-%d')
        self.calendar.add_to_calendar('Reminder Test', today, reminder_days=0)
        reminders = self.calendar.get_reminders()
        self.assertEqual(len(reminders), 1)

if __name__ == '__main__':
    unittest.main()
