import unittest
import logging
from unittest.mock import patch
from agents.core.utilities.AgentBase import AgentBase

class MockAgent(AgentBase):
    """Mock implementation of AgentBase for testing."""

    def solve_task(self, task: str, **kwargs):
        return f"MockAgent solved task: {task}"

    def describe_capabilities(self):
        return "Mock agent for testing."

class TestAgentBase(unittest.TestCase):
    """Unit tests for the AgentBase abstract class."""

    def setUp(self):
        """Set up a mock agent instance for testing."""
        self.agent = MockAgent(name="MockAgent", project_name="TestProject")

    def test_initialization(self):
        """Test if the AgentBase initializes correctly."""
        self.assertEqual(self.agent.name, "MockAgent")
        self.assertEqual(self.agent.project_name, "TestProject")

    def test_solve_task_mock(self):
        """Test that solve_task runs correctly in a mock implementation."""
        result = self.agent.solve_task("Test Task")
        self.assertIn("MockAgent solved task: Test Task", result)

    def test_describe_capabilities(self):
        """Test the describe_capabilities method."""
        result = self.agent.describe_capabilities()
        self.assertIn("Mock agent for testing.", result)

    def test_shutdown(self):
        """Test that shutdown logs properly."""
        with self.assertLogs(level="INFO") as log:
            self.agent.shutdown()
            self.assertTrue(any("Shutting down agent 'MockAgent'" in msg for msg in log.output))

if __name__ == "__main__":
    unittest.main()
