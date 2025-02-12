# content_calendar.py

import json
import os
from datetime import datetime

class ContentCalendar:
    def __init__(self, storage_path='data/content_calendar.json'):
        self.storage_path = storage_path
        self.calendar = self._load_calendar()

    def _load_calendar(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as file:
                return json.load(file)
        return []

    def _save_calendar(self):
        with open(self.storage_path, 'w') as file:
            json.dump(self.calendar, file, indent=4)

    def add_to_calendar(self, title, scheduled_date):
        event = {
            'id': len(self.calendar) + 1,
            'title': title,
            'scheduled_date': scheduled_date,
            'created_at': datetime.now().isoformat()
        }
        self.calendar.append(event)
        self._save_calendar()
        return event

    def get_scheduled_content(self, date=None):
        if date:
            return [event for event in self.calendar if event['scheduled_date'] == date]
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

# Tests for ContentCalendar
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

if __name__ == '__main__':
    unittest.main()
