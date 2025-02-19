"""

Module for unit testing the JournalAgent class. This module tests functions such as 
create_journal_entry, retrieve_journal_entry, update_journal_entry, delete_journal_entry 
and list_journal_entries. It also tests various task actions such as create, retrieve, 
update, delete and handling of invalid actions. Each function and task is tested under 
normal conditions as well as various edge-case conditions.

"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

from agents.core.journal_agent import JournalAgent  # Use JournalAgent directly


class TestJournalAgent(unittest.TestCase):
    def setUp(self):
        self.agent = JournalAgent(journal_directory="test_journals")
        os.makedirs("test_journals", exist_ok=True)

    def tearDown(self):
        for file in os.listdir("test_journals"):
            os.remove(os.path.join("test_journals", file))
        os.rmdir("test_journals")

    def test_create_journal_entry(self):
        result = self.agent.create_journal_entry("test", "content")
        self.assertEqual(result["status"], "success")

    def test_retrieve_journal_entry(self):
        """Test retrieving an existing journal entry."""
        self.agent.create_journal_entry("Test Entry", "This is a test.", ["test"])
        result = self.agent.retrieve_journal_entry("Test Entry")
        self.assertIn("entry", result)
        self.assertEqual(result["entry"]["content"], "This is a test.")

        def test_create_journal_entry(self):
        result = self.agent.create_journal_entry("test", "content")
        self.assertEqual(result["status"], "success")

    def test_update_journal_entry(self):
        self.agent.create_journal_entry("test", "content")
        result = self.agent.update_journal_entry("test", "new content")
        self.assertEqual(result["status"], "success")

    def test_delete_journal_entry(self):
        self.agent.create_journal_entry("test", "content")
        result = self.agent.delete_journal_entry("test")
        self.assertEqual(result["status"], "success")

    def test_list_journal_entries(self):
        self.agent.create_journal_entry("test1", "content")
        self.agent.create_journal_entry("test2", "content")
        result = self.agent.list_journal_entries()
        self.assertEqual(len(result["entries"]), 2)


    def test_perform_task_create(self):
        """Test performing a 'create' task."""
        result = self.agent.solve_task(
            "create", title="Task Entry", content="Created via task", tags=["task"]
        )
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")

    def test_perform_task_retrieve(self):
        """Test performing a 'retrieve' task."""
        self.agent.create_journal_entry("Task Entry", "Task-based retrieval")
        result = self.agent.solve_task("retrieve", title="Task Entry")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")

    def test_perform_task_update(self):
        """Test performing an 'update' task."""
        self.agent.create_journal_entry("Task Entry", "Initial content")
        result = self.agent.solve_task("update", title="Task Entry", new_content="Updated via task")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")

    def test_perform_task_delete(self):
        """Test performing a 'delete' task."""
        self.agent.create_journal_entry("Task Entry", "Content to delete")
        result = self.agent.solve_task("delete", title="Task Entry")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")

    def test_perform_task_invalid_action(self):
        """Test handling of an invalid action."""
        result = self.agent.solve_task("invalid_action")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()
