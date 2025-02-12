# core/idea_integrator.py
from core.idea_vault import IdeaVault
from datetime import datetime

class IdeaIntegrator:
    def __init__(self):
        self.idea_vault = IdeaVault()

    def suggest_optimal_schedule(self, idea_id):
        idea = next((idea for idea in self.idea_vault.get_ideas() if idea['id'] == idea_id), None)
        if idea:
            return f"Scheduled for {datetime.now().isoformat()}"
        return None

    def push_idea_to_schedule(self, idea_id):
        schedule_time = self.suggest_optimal_schedule(idea_id)
        if schedule_time:
            updated_idea = self.idea_vault.update_idea(idea_id, status='scheduled', scheduled_time=schedule_time)
            return updated_idea
        return None

# Unit Tests
import unittest
import os

class TestIdeaIntegrator(unittest.TestCase):
    def setUp(self):
        self.integrator = IdeaIntegrator()
        self.vault = self.integrator.idea_vault
        self.vault.ideas = []
        self.vault._save_ideas()

    def tearDown(self):
        if os.path.exists('data/idea_vault.json'):
            os.remove('data/idea_vault.json')

    def test_suggest_optimal_schedule(self):
        idea = self.vault.add_idea('Test Idea', 'Description')
        schedule = self.integrator.suggest_optimal_schedule(idea['id'])
        self.assertIsNotNone(schedule)

    def test_push_idea_to_schedule(self):
        idea = self.vault.add_idea('Another Idea', 'Description')
        updated_idea = self.integrator.push_idea_to_schedule(idea['id'])
        self.assertEqual(updated_idea['status'], 'scheduled')

if __name__ == '__main__':
    unittest.main()
