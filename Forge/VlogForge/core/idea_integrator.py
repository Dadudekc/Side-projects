# core/idea_integrator.py
from core.idea_vault import IdeaVault
from datetime import datetime
from core.social_media_analyzer import SocialMediaAnalyzer

class IdeaIntegrator:
    def __init__(self):
        self.idea_vault = IdeaVault()
        self.social_media_analyzer = SocialMediaAnalyzer()

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

    def analyze_social_sentiment(self, idea_id):
        idea = next((idea for idea in self.idea_vault.get_ideas() if idea['id'] == idea_id), None)
        if idea:
            sentiment_data = self.social_media_analyzer.scrape_stocktwits_post(idea['title'], idea['description'])
            return sentiment_data
        return None

# Unit Tests
import unittest
import os
from unittest.mock import patch, MagicMock

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

    @patch('core.social_media_analyzer.SocialMediaAnalyzer.scrape_stocktwits_post')
    def test_analyze_social_sentiment(self, mock_scrape):
        mock_scrape.return_value = {'title': 'AAPL', 'description': 'Test description', 'post': 'Positive sentiment!', 'sentiment': 0.8}
        idea = self.vault.add_idea('AAPL', 'Analyze sentiment for Apple stock.')
        sentiment_data = self.integrator.analyze_social_sentiment(idea['id'])
        self.assertIsNotNone(sentiment_data)
        self.assertEqual(sentiment_data['sentiment'], 0.8)

if __name__ == '__main__':
    unittest.main()
