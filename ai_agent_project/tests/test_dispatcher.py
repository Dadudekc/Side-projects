import unittest
import json
from agents.core.AgentDispatcher import AgentDispatcher

class TestAgentDispatcher(unittest.TestCase):
    """Unit tests for AgentDispatcher."""

    def setUp(self):
        """Initialize the agent dispatcher before each test."""
        self.dispatcher = AgentDispatcher()

    def test_dispatch_valid_agent(self):
        """Test dispatching a task to a valid agent."""
        task_data = {
            "action": "create",
            "title": "Test Journal",
            "content": "Test content"
        }

        # Get the response from the dispatcher
        result = self.dispatcher.dispatch_task("JournalAgent", task_data)

        # Ensure result is a string (since we convert dicts to JSON strings)
        self.assertIsInstance(result, str)

        # Convert result to a dictionary
        try:
            result_data = json.loads(result)
        except json.JSONDecodeError:
            self.fail("AgentDispatcher did not return a valid JSON string.")

        # Ensure status is "success"
        self.assertEqual(result_data.get("status"), "success", "JournalAgent did not process the task correctly.")

if __name__ == "__main__":
    unittest.main()
