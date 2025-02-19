"""
Unit tests for the AgentRegistry class.

Tests:
- Ensures the AgentRegistry can register and retrieve agents.
- Validates correct loading of agents.
- Checks if the list_agents() function correctly returns registered agent names.
"""

import unittest
from unittest.mock import MagicMock
from agents.core.agent_registry import AgentRegistry


class MockAgent:
    """Mock implementation of an agent for testing purposes."""

    def __init__(self):
        self.name = "MockAgent"

    def solve_task(self, task: str, **kwargs):
        """Simulates solving a given task."""
        return f"Task '{task}' solved."

    def describe_capabilities(self) -> str:
        """Returns a description of the agent's capabilities."""
        return "Mock agent capabilities."


class TestAgentRegistry(unittest.TestCase):
    """Unit tests for the AgentRegistry class."""

    def setUp(self):
        """Set up a fresh AgentRegistry instance for each test."""
        self.registry = AgentRegistry()
        self.mock_agent = MockAgent()

        # Explicitly register mock agents
        self.registry.register_agent("JournalAgent", self.mock_agent)
        self.registry.register_agent("TradingAgent", self.mock_agent)
        self.registry.register_agent("DebuggerAgent", self.mock_agent)

    def test_load_agents(self):
        """Test if agents are correctly loaded into the registry."""
        agents_list = self.registry.list_agents()
        self.assertIn("JournalAgent", agents_list)
        self.assertIn("TradingAgent", agents_list)
        self.assertIn("DebuggerAgent", agents_list)

    def test_get_agent(self):
        """Test retrieving an agent by name."""
        agent = self.registry.get_agent("JournalAgent")
        self.assertIsInstance(agent, MockAgent)

    def test_list_agents(self):
        """Test listing registered agents."""
        agents_list = self.registry.list_agents()
        expected_agents = {"JournalAgent", "TradingAgent", "DebuggerAgent"}
        self.assertEqual(set(agents_list), expected_agents)

    def test_unregister_agent(self):
        """Test unregistering an agent."""
        self.registry.unregister_agent("JournalAgent")
        self.assertNotIn("JournalAgent", self.registry.list_agents())

    def test_register_duplicate_agent(self):
        """Test attempting to register an agent that already exists."""
        result = self.registry.register_agent("JournalAgent", self.mock_agent)
        self.assertFalse(result)  # Should return False as the agent is already registered

    def test_agent_exists(self):
        """Test checking if an agent exists in the registry."""
        self.assertTrue(self.registry.agent_exists("DebuggerAgent"))
        self.assertFalse(self.registry.agent_exists("NonExistentAgent"))


if __name__ == "__main__":
    unittest.main()
