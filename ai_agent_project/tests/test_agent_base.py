import unittest

from agents.core.utilities.AgentBase import AgentBase


class MockAgent(AgentBase):
    """A mock implementation of AgentBase for testing purposes."""

    def solve_task(self, task: str, **kwargs):
        """Solves the given task and returns a confirmation message."""
        return f"Task '{task}' solved."

    def describe_capabilities(self) -> str:
        """Returns a description of the agent's capabilities."""
        return "Mock agent capabilities."


class TestAgentBase(unittest.TestCase):
    """Unit tests for the AgentBase class."""

    def setUp(self):
        """Setup method to create a test agent instance."""
        self.agent = MockAgent(name="TestAgent", project_name="TestProject")

    def test_initialization(self):
        """Test if the agent initializes correctly."""
        self.assertEqual(self.agent.name, "TestAgent")
        self.assertEqual(self.agent.project_name, "TestProject")

    def test_solve_task(self):
        """Test the solve_task method."""
        result = self.agent.solve_task("SampleTask")
        self.assertEqual(result, "Task 'SampleTask' solved.")

    def test_describe_capabilities(self):
        """Test the describe_capabilities method."""
        self.assertEqual(self.agent.describe_capabilities(), "Mock agent capabilities.")

    def test_shutdown(self):
        """Test the shutdown method."""
        # Ensure it doesn't raise any errors
        try:
            self.agent.shutdown()
        except Exception as e:
            self.fail(f"shutdown() method raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
