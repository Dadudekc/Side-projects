# core/idea_vault.py
import json
import os
from datetime import datetime
import unittest

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

# Unit Tests
class TestIdeaVault(unittest.TestCase):
    def setUp(self):
        self.vault = IdeaVault('test_idea_vault.json')
        self.vault.ideas = []  # Clear existing ideas
        self.vault._save_ideas()

    def tearDown(self):
        if os.path.exists('test_idea_vault.json'):
            os.remove('test_idea_vault.json')

    def test_add_idea(self):
        idea = self.vault.add_idea('Test Idea', 'Test Description')
        self.assertEqual(idea['title'], 'Test Idea')
        self.assertEqual(idea['description'], 'Test Description')

    def test_get_ideas(self):
        self.vault.add_idea('Idea 1', 'Desc 1')
        self.vault.add_idea('Idea 2', 'Desc 2')
        ideas = self.vault.get_ideas()
        self.assertEqual(len(ideas), 2)

    def test_update_idea(self):
        idea = self.vault.add_idea('Old Title', 'Old Description')
        updated_idea = self.vault.update_idea(idea['id'], title='New Title')
        self.assertEqual(updated_idea['title'], 'New Title')

    def test_delete_idea(self):
        idea = self.vault.add_idea('Delete Me', 'To be deleted')
        self.vault.delete_idea(idea['id'])
        self.assertEqual(len(self.vault.get_ideas()), 0)

    def test_search_ideas(self):
        self.vault.add_idea('Search This', 'Contains keyword')
        results = self.vault.search_ideas('Search')
        self.assertEqual(len(results), 1)

    def test_filter_by_tags(self):
        self.vault.add_idea('Tagged Idea', 'Desc', tags=['tag1', 'tag2'])
        results = self.vault.filter_by_tags(['tag1'])
        self.assertEqual(len(results), 1)

if __name__ == '__main__':
    unittest.main()
