# idea_vault.py

import json
import os
from datetime import datetime

class IdeaVault:
    def __init__(self, storage_path='data/idea_vault.json'):
        self.storage_path = storage_path
        self.ideas = self._load_ideas()

    def _load_ideas(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as file:
                return json.load(file)
        return []

    def _save_ideas(self):
        with open(self.storage_path, 'w') as file:
            json.dump(self.ideas, file, indent=4)

    def add_idea(self, title, description, tags=None):
        idea = {
            'id': len(self.ideas) + 1,
            'title': title,
            'description': description,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'status': 'new'
        }
        self.ideas.append(idea)
        self._save_ideas()
        return idea

    def get_ideas(self, status=None):
        if status:
            return [idea for idea in self.ideas if idea['status'] == status]
        return self.ideas

    def update_idea(self, idea_id, **kwargs):
        for idea in self.ideas:
            if idea['id'] == idea_id:
                idea.update(kwargs)
                self._save_ideas()
                return idea
        return None

    def delete_idea(self, idea_id):
        self.ideas = [idea for idea in self.ideas if idea['id'] != idea_id]
        self._save_ideas()

    def search_ideas(self, keyword):
        return [idea for idea in self.ideas if keyword.lower() in idea['title'].lower() or keyword.lower() in idea['description'].lower()]

    def filter_by_tags(self, tags):
        return [idea for idea in self.ideas if any(tag in idea['tags'] for tag in tags)]

# Integration with other Vlog Forge modules
from core.content_manager import ContentManager
from ui.content_calendar import ContentCalendar
from core.engagement_tracker import EngagementTracker
from core.auto_posting import AutoPostScheduler

class IdeaIntegrator:
    def __init__(self, idea_vault, content_manager, content_calendar, engagement_tracker, auto_posting):
        self.idea_vault = idea_vault
        self.content_manager = content_manager
        self.content_calendar = content_calendar
        self.engagement_tracker = engagement_tracker
        self.auto_posting = auto_posting

    def suggest_optimal_schedule(self, idea_id):
        idea = next((idea for idea in self.idea_vault.ideas if idea['id'] == idea_id), None)
        if idea:
            engagement_data = self.engagement_tracker.get_best_times()
            return engagement_data.get('optimal_time', datetime.now().isoformat())
        return None

    def push_idea_to_schedule(self, idea_id, scheduled_date=None):
        if not scheduled_date:
            scheduled_date = self.suggest_optimal_schedule(idea_id)

        idea = self.idea_vault.update_idea(idea_id, status='scheduled')
        if idea:
            self.content_manager.schedule_content(idea['title'], idea['description'], scheduled_date)
            self.content_calendar.add_to_calendar(idea['title'], scheduled_date)
            self.auto_posting.schedule_post(idea['title'], idea['description'], scheduled_date)
            self.auto_posting.schedule_instagram_post(idea['title'], idea['description'], scheduled_date)
            self.auto_posting.schedule_linkedin_post(idea['title'], idea['description'], scheduled_date)
            self.auto_posting.schedule_tiktok_post(idea['title'], idea['description'], scheduled_date)
            self.auto_posting.schedule_facebook_post(idea['title'], idea['description'], scheduled_date)
            return True
        return False

    def track_idea_performance(self, idea_id):
        idea = next((idea for idea in self.idea_vault.ideas if idea['id'] == idea_id), None)
        if idea:
            performance_data = self.engagement_tracker.get_performance_metrics(idea['title'])
            return performance_data
        return None

# Tests for IdeaVault
import unittest
from unittest.mock import MagicMock

class TestIdeaVault(unittest.TestCase):
    def setUp(self):
        self.vault = IdeaVault('test_idea_vault.json')
        self.vault.ideas = []  # Clear test data
        self.vault._save_ideas()

        # Mock dependencies
        self.content_manager = MagicMock()
        self.content_calendar = MagicMock()
        self.engagement_tracker = MagicMock()
        self.auto_posting = MagicMock()

        self.integrator = IdeaIntegrator(
            self.vault, self.content_manager, self.content_calendar, self.engagement_tracker, self.auto_posting
        )

    def tearDown(self):
        os.remove('test_idea_vault.json')

    def test_add_idea(self):
        idea = self.vault.add_idea('Test Idea', 'This is a test description.')
        self.assertEqual(idea['title'], 'Test Idea')
        self.assertEqual(idea['description'], 'This is a test description.')

    def test_get_ideas(self):
        self.vault.add_idea('Idea 1', 'Desc 1')
        self.vault.add_idea('Idea 2', 'Desc 2', tags=['tag1'])
        ideas = self.vault.get_ideas()
        self.assertEqual(len(ideas), 2)

    def test_update_idea(self):
        idea = self.vault.add_idea('Update Test', 'Old Description')
        updated_idea = self.vault.update_idea(idea['id'], description='New Description')
        self.assertEqual(updated_idea['description'], 'New Description')

    def test_delete_idea(self):
        idea = self.vault.add_idea('Delete Test', 'To be deleted')
        self.vault.delete_idea(idea['id'])
        ideas = self.vault.get_ideas()
        self.assertEqual(len(ideas), 0)

    def test_search_ideas(self):
        self.vault.add_idea('Keyword Test', 'This idea contains the keyword.')
        results = self.vault.search_ideas('keyword')
        self.assertEqual(len(results), 1)

    def test_filter_by_tags(self):
        self.vault.add_idea('Tag Test 1', 'Description', tags=['video', 'content'])
        self.vault.add_idea('Tag Test 2', 'Description', tags=['blog'])
        results = self.vault.filter_by_tags(['content'])
        self.assertEqual(len(results), 1)

    def test_dynamic_scheduling(self):
        idea = self.vault.add_idea('Dynamic Schedule Test', 'Automated scheduling based on engagement.')

        # Mock optimal time
        self.engagement_tracker.get_best_times.return_value = {'optimal_time': '2024-02-21T10:00:00'}

        result = self.integrator.push_idea_to_schedule(idea['id'])
        self.assertTrue(result)

        self.content_manager.schedule_content.assert_called_with(
            idea['title'], idea['description'], '2024-02-21T10:00:00'
        )
        self.content_calendar.add_to_calendar.assert_called_with(
            idea['title'], '2024-02-21T10:00:00'
        )
        self.auto_posting.schedule_post.assert_called_with(
            idea['title'], idea['description'], '2024-02-21T10:00:00'
        )
        self.auto_posting.schedule_instagram_post.assert_called_with(
            idea['title'], idea['description'], '2024-02-21T10:00:00'
        )
        self.auto_posting.schedule_linkedin_post.assert_called_with(
            idea['title'], idea['description'], '2024-02-21T10:00:00'
        )
        self.auto_posting.schedule_tiktok_post.assert_called_with(
            idea['title'], idea['description'], '2024-02-21T10:00:00'
        )
        self.auto_posting.schedule_facebook_post.assert_called_with(
            idea['title'], idea['description'], '2024-02-21T10:00:00'
        )

if __name__ == '__main__':
    unittest.main()

# Initialize the components
idea_vault = IdeaVault('data/idea_vault.json')
content_manager = ContentManager()
content_calendar = ContentCalendar()
engagement_tracker = EngagementTracker()
auto_posting = AutoPosting()

# Create the integrator
idea_integrator = IdeaIntegrator(
    idea_vault,
    content_manager,
    content_calendar,
    engagement_tracker,
    auto_posting
)

# Example usage
# Add a new idea
new_idea = idea_vault.add_idea(
    title="New Marketing Strategy",
    description="Develop a new strategy for social media marketing.",
    tags=["marketing", "strategy"]
)

# Suggest an optimal schedule for the idea
optimal_schedule = idea_integrator.suggest_optimal_schedule(new_idea['id'])
print(f"Optimal schedule for the idea: {optimal_schedule}")

# Push the idea to the schedule
success = idea_integrator.push_idea_to_schedule(new_idea['id'])
if success:
    print("Idea successfully scheduled.")
else:
    print("Failed to schedule the idea.")

# Track the performance of the idea
performance_data = idea_integrator.track_idea_performance(new_idea['id'])
print(f"Performance data: {performance_data}")
