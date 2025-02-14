# test_ai_agent.py

"""
Unit Tests for AIAgentWithMemory Class

Tests the functionality of the AIAgentWithMemory class, including interaction
with the MemoryManager and handling of AI responses. Mocks external subprocess
calls to the AI model to ensure tests are deterministic.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
from AI_Debugger_Assistant.ai_agent_project.src.ai_agent_utils import AIAgentWithMemory
from ai_agent_project.src.agents.core.utilities.memory_manager import MemoryManager

class TestAIAgentWithMemory(unittest.TestCase):
    def setUp(self):
        """
        Set up a fresh MemoryManager and AIAgentWithMemory instance before each test.
        """
        self.test_db = "test_ai_agent_memory.db"
        self.memory_manager = MemoryManager(db_path=self.test_db, table_name="test_memory_entries")
        self.agent = AIAgentWithMemory("TestAgent", "TestProject", self.memory_manager)

    def tearDown(self):
        """
        Clean up by removing the test database after each test.
        """
        self.memory_manager.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    @patch('subprocess.run')
    def test_chat_response(self, mock_subprocess_run):
        """
        Test that the chat method returns the AI's response correctly.
        """
        # Mock the subprocess.run to return a predefined response
        mock_result = MagicMock()
        mock_result.stdout = "Hi there! How can I assist you today?"
        mock_subprocess_run.return_value = mock_result

        response = self.agent.chat("Hello")
        self.assertEqual(response, "Hi there! How can I assist you today!")

        # Ensure that the memory was saved correctly
        context = self.memory_manager.retrieve_memory("TestProject", limit=1)
        self.assertIn("Hello", context)
        self.assertIn("Hi there! How can I assist you today!", context)

    @patch('subprocess.run')
    def test_run_query_subprocess_error(self, mock_subprocess_run):
        """
        Test that run_query handles subprocess errors gracefully.
        """
        # Configure the mock to raise a CalledProcessError
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd='ollama run mistral',
            stderr='AI model error'
        )

        response = self.agent.chat("Hello")
        self.assertIn("An error occurred while communicating with Ollama: AI model error", response)

    @patch('subprocess.run')
    def test_run_query_unexpected_error(self, mock_subprocess_run):
        """
        Test that run_query handles unexpected exceptions gracefully.
        """
        # Configure the mock to raise a generic exception
        mock_subprocess_run.side_effect = Exception("Unexpected error")

        response = self.agent.chat("Hello")
        self.assertIn("An unexpected error occurred: Unexpected error", response)

if __name__ == '__main__':
    unittest.main()
