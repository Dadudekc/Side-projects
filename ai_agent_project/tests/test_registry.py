"""

Module for creating a mock agent and performing unit tests on the AgentRegistry class methods. 

The MockAgent class is a simulation of a real agent. This class inherits from AgentBase class and implemented for testing purposes.

The TestAgentRegistry class is a subclass of unittest.TestCase for defining unit tests for the AgentRegistry class.
It provides setUp method for initializing the agent registry before each test and several test methods:
- test_get_invalid_agent: Test retrieving a non-existent agent.
- test_get_valid_agent
"""

import unittest
from agents.core.agent_registry import AgentRegistry
from agents.core.AgentBase import AgentBase

class MockAgent(AgentBase):
    """Mock agent for testing registration and unregistration."""
    def describe_capabilities(self) -> str:
        return "Mock agent for testing."

    def solve_task(self, task: str, **kwargs):
        return {"status": "success", "message": f"MockAgent handled '{task}'"}

class TestAgentRegistry(unittest.TestCase):
    """Unit tests for the AgentRegistry class."""

    def setUp(self):
        """Initialize the agent registry before each test."""
        self.registry = AgentRegistry()



    def test_get_valid_agent(self):
        """Test retrieving a valid agent."""
        agent = self.registry.get_agent("JournalAgent")
        self.assertIsNotNone(agent, "JournalAgent not found in registry.")



    def test_register_agent(self):
        """Test registering a new agent."""
        mock_agent = MockAgent(name="MockAgent", project_name="TestProject")
        result = self.registry.register_agent("MockAgent", mock_agent)
        self.assertTrue(result, "MockAgent should be registered successfully.")
        self.assertIn("MockAgent", self.registry.list_agents(), "MockAgent not found after registration.")

    def test_register_duplicate_agent(self):
        """Test that registering the same agent twice fails."""
        mock_agent = MockAgent(name="MockAgent", project_name="TestProject")
        self.registry.register_agent("MockAgent", mock_agent)
        result = self.registry.register_agent("MockAgent", mock_agent)
        self.assertFalse(result, "Duplicate agent registration should fail.")

    def test_unregister_agent(self):
        """Test unregistering an existing agent."""
        mock_agent = MockAgent(name="MockAgent", project_name="TestProject")
        self.registry.register_agent("MockAgent", mock_agent)
        result = self.registry.unregister_agent("MockAgent")
        self.assertTrue(result, "MockAgent should be unregistered successfully.")
        self.assertNotIn("MockAgent", self.registry.list_agents(), "MockAgent should not exist after unregistration.")

    def test_unregister_nonexistent_agent(self):
        """Test unregistering a non-existent agent."""
        result = self.registry.unregister_agent("NonExistentAgent")
        self.assertFalse(result, "Unregistering a non-existent agent should fail.")

    def test_get_valid_agent(self):
        """Test retrieving a valid agent."""
        agent = self.registry.get_agent("JournalAgent")
        self.assertIsNotNone(agent, "JournalAgent not found in registry.")

    def test_list_agents(self):
        """Test that agents are loaded correctly."""
        agents = self.registry.list_agents()
        self.assertIn("JournalAgent", agents, "JournalAgent should be in the registry.")

    def test_agent_exists(self):
        """Test checking if an agent exists."""
        self.assertTrue(self.registry.agent_exists("JournalAgent"), "JournalAgent should exist in registry.")


if __name__ == "__main__":
    unittest.main()
