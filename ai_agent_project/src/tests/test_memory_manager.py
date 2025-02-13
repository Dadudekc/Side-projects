# test_memory_manager.py

"""
Unit Tests for MemoryManager Class

Tests the functionality of the MemoryManager class, including saving and retrieving
memory entries, ensuring data integrity, and handling edge cases.
"""

import unittest
import os
from ai_agent_project.src.agents.core.utilities.memory_manager import MemoryManager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        """
        Set up a fresh MemoryManager instance with a test database before each test.
        """
        self.test_db = "test_memory.db"
        self.memory_manager = MemoryManager(db_path=self.test_db, table_name="test_memory_entries")

    def tearDown(self):
        """
        Clean up by removing the test database after each test.
        """
        self.memory_manager.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_save_and_retrieve_memory(self):
        """
        Test that memory entries can be saved and retrieved correctly.
        """
        self.memory_manager.save_memory("TestProject", "Hello", "Hi there!")
        context = self.memory_manager.retrieve_memory("TestProject", limit=1)
        self.assertIn("Hello", context)
        self.assertIn("Hi there!", context)

    def test_retrieve_memory_limit(self):
        """
        Test that the retrieve_memory method respects the limit parameter.
        """
        for i in range(10):
            self.memory_manager.save_memory("TestProject", f"Prompt {i}", f"Response {i}")
        context = self.memory_manager.retrieve_memory("TestProject", limit=5)
        for i in range(5, 10):
            self.assertIn(f"Prompt {i}", context)
            self.assertIn(f"Response {i}", context)
        self.assertNotIn("Prompt 4", context)

    def test_delete_memory_older_than(self):
        """
        Test that memory entries older than a specified number of days are deleted.
        """
        # Save a memory entry
        self.memory_manager.save_memory("TestProject", "Old Prompt", "Old Response")
        
        # Manually update the timestamp to 31 days ago
        with self.memory_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
            UPDATE {self.memory_manager.table_name}
            SET timestamp = datetime('now', '-31 days')
            WHERE user_prompt = 'Old Prompt';
            """)
            conn.commit()
        
        # Delete entries older than 30 days
        self.memory_manager.delete_memory_older_than("TestProject", days=30)
        
        # Retrieve memories to ensure deletion
        context = self.memory_manager.retrieve_memory("TestProject", limit=10)
        self.assertNotIn("Old Prompt", context)

    def test_retrieve_memory_no_entries(self):
        """
        Test that retrieving memory for a project with no entries returns an empty string.
        """
        context = self.memory_manager.retrieve_memory("NonExistentProject", limit=5)
        self.assertEqual(context, "")

if __name__ == '__main__':
    unittest.main()
