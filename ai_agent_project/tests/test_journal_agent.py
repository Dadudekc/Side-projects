import json
import os
import unittest
from unittest.mock import MagicMock, patch

from agents.core.JournalAgent import JournalAgent  # Use JournalAgent directly


class TestJournalAgent(unittest.TestCase):
    """Unit tests for the JournalAgent class."""

    def setUp(self):
        """Setup test environment by creating a temporary journal directory."""
        self.journal_dir = "test_journals"
        self.agent = JournalAgent(journal_directory=self.journal_dir)
        os.makedirs(self.journal_dir, exist_ok=True)

    def tearDown(self):
        """Cleanup after tests by deleting the test journal directory."""
        for file in os.listdir(self.journal_dir):
            os.remove(os.path.join(self.journal_dir, file))
        os.rmdir(self.journal_dir)

    def test_create_journal_entry(self):
        """Test creating a journal entry."""
        result = self.agent.create_journal_entry(
            "Test Entry", "This is a test.", ["test", "entry"]
        )
        self.assertIn("file_path", result)
        self.assertTrue(os.path.exists(result["file_path"]))

    def test_retrieve_journal_entry(self):
        """Test retrieving an existing journal entry."""
        self.agent.create_journal_entry("Test Entry", "This is a test.", ["test"])
        result = self.agent.retrieve_journal_entry("Test Entry")
        self.assertIn("entry", result)
        self.assertEqual(result["entry"]["content"], "This is a test.")

    def test_update_journal_entry(self):
        """Test updating an existing journal entry."""
        self.agent.create_journal_entry("Test Entry", "Initial content.")
        result = self.agent.update_journal_entry("Test Entry", "Updated content.")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")

        retrieved = self.agent.retrieve_journal_entry("Test Entry")
        self.assertIn("entry", retrieved)
        self.assertEqual(retrieved["entry"]["content"], "Updated content.")

    def test_delete_journal_entry(self):
        """Test deleting a journal entry."""
        self.agent.create_journal_entry("Test Entry", "This will be deleted.")
        result = self.agent.delete_journal_entry("Test Entry")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")

        retrieved = self.agent.retrieve_journal_entry("Test Entry")
        self.assertIn("status", retrieved)
        self.assertEqual(retrieved["status"], "error")

    def test_list_journal_entries(self):
        """Test listing all journal entries."""
        self.agent.create_journal_entry("Entry 1", "Content 1")
        self.agent.create_journal_entry("Entry 2", "Content 2")
        result = self.agent.list_journal_entries()
        self.assertIn("entries", result)
        self.assertGreaterEqual(len(result["entries"]), 2)

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
