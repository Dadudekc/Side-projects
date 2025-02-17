import unittest

from agents.core.agent_registry import AgentRegistry


class TestAgentRegistry(unittest.TestCase):
    """Unit tests for the AgentRegistry class."""

    def setUp(self):
        """Initialize the agent registry before each test."""
        self.registry = AgentRegistry()

    def test_get_invalid_agent(self):
        """Test retrieving a non-existent agent."""
        agent = self.registry.get_agent("NonExistentAgent")
        self.assertIsNone(agent, "Non-existent agent should return None.")

    def test_get_valid_agent(self):
        """Test retrieving a valid agent."""
        agent = self.registry.get_agent("JournalAgent")
        self.assertIsNotNone(agent, "JournalAgent not found in registry.")

    def test_load_agents(self):
        """Test that agents are loaded correctly."""
        agents = self.registry.list_agents()
        self.assertIn("JournalAgent", agents, "JournalAgent should be in the registry.")


if __name__ == "__main__":
    unittest.main()
