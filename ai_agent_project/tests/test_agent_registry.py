"""
Unit tests for the AgentRegistry class.

Tests:
- Ensures the AgentRegistry can register, retrieve, and unregister agents.
- Validates correct loading of agents.
- Checks if the list_agents() function correctly returns registered agent names.
- Ensures that duplicate agent registration fails.
- Confirms proper handling of non-existent agents.

MockAgent:
- A subclass of AgentBase, simulating a real agent for testing.
- Implements basic capabilities and task-solving for validation.
"""

import unittest
from unittest.mock import patch
from agents.core.agent_registry import AgentRegistry
from agents.core.AgentBase import AgentBase


class MockAgent(AgentBase):
    """Mock implementation of an agent for testing purposes."""

    def describe_capabilities(self) -> str:
        """Returns a description of the agent's capabilities."""
        return "Mock agent for testing."

    def solve_task(self, task: str, **kwargs):
        """Simulates solving a given task."""
        return {"status": "success", "message": f"MockAgent handled '{task}'"}


class TestAgentRegistry(unittest.TestCase):
    """Unit tests for the AgentRegistry class."""

    @patch.object(AgentRegistry, "load_core_agents", lambda self: None)  # Prevents default agents from loading
    def setUp(self):
        """Set up a fresh AgentRegistry instance for each test."""
        self.registry = AgentRegistry()  # Now it won't load default agents
        self.mock_agent = MockAgent(name="MockAgent", project_name="TestProject")

        # Register mock agents explicitly
        self.registry.register_agent("JournalAgent", self.mock_agent)
        self.registry.register_agent("TradingAgent", self.mock_agent)
        self.registry.register_agent("DebuggerAgent", self.mock_agent)

    def test_load_agents(self):
        """Test if agents are correctly loaded into the registry."""
        agents_list = self.registry.list_agents()
        self.assertIn("JournalAgent", agents_list)
        self.assertIn("TradingAgent", agents_list)
        self.assertIn("DebuggerAgent", agents_list)

    def test_get_valid_agent(self):
        """Test retrieving a valid agent."""
        agent = self.registry.get_agent("JournalAgent")
        self.assertIsInstance(agent, MockAgent)

    def test_get_invalid_agent(self):
        """Test retrieving a non-existent agent."""
        agent = self.registry.get_agent("NonExistentAgent")
        self.assertIsNone(agent, "Non-existent agent should return None.")

    def test_list_agents(self):
        """Test that agents are listed correctly."""
        agents_list = self.registry.list_agents()
        expected_agents = {"JournalAgent", "TradingAgent", "DebuggerAgent"}
        self.assertEqual(set(agents_list), expected_agents)

    def test_register_agent(self):
        """Test registering a new agent."""
        new_agent = MockAgent(name="NewAgent", project_name="TestProject")
        result = self.registry.register_agent("NewAgent", new_agent)
        self.assertTrue(result, "NewAgent should be registered successfully.")
        self.assertIn("NewAgent", self.registry.list_agents(), "NewAgent not found after registration.")

    def test_register_duplicate_agent(self):
        """Test that registering the same agent twice fails."""
        result = self.registry.register_agent("JournalAgent", self.mock_agent)
        self.assertFalse(result, "Duplicate agent registration should fail.")

    def test_unregister_agent(self):
        """Test unregistering an existing agent."""
        result = self.registry.unregister_agent("JournalAgent")
        self.assertTrue(result, "JournalAgent should be unregistered successfully.")
        self.assertNotIn("JournalAgent", self.registry.list_agents(), "JournalAgent should not exist after unregistration.")

    def test_unregister_nonexistent_agent(self):
        """Test unregistering a non-existent agent."""
        result = self.registry.unregister_agent("NonExistentAgent")
        self.assertFalse(result, "Unregistering a non-existent agent should fail.")

    def test_agent_exists(self):
        """Test checking if an agent exists."""
        self.assertTrue(self.registry.agent_exists("DebuggerAgent"), "DebuggerAgent should exist in registry.")
        self.assertFalse(self.registry.agent_exists("FakeAgent"), "FakeAgent should not exist in registry.")


if __name__ == "__main__":
    unittest.main()
