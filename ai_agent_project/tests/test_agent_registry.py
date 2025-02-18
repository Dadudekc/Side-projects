"""

A module for testing the AgentRegistry class from the agents.core.agent_registry module.

This module includes a unit test suite composed by the class TestAgentRegistry which tests functionalities of
the AgentRegistry class.

MockAgent class:
    A mock class used for creating fake agents in the context of the tests.

TestAgentRegistry class:
    A subclass of the unittest.TestCase, tailored for testing the AgentRegistry class.

TestAgentRegistry methods:
    - setUp: prepares the requirements before each test.
    -
"""

import unittest
from unittest.mock import MagicMock, patch
import importlib

from agents.core.agent_registry import AgentRegistry


class MockAgent:
    """Mock implementation of an agent for testing purposes."""

    def solve_task(self, task: str, **kwargs):
        """Simulates solving a given task."""
        return f"Task '{task}' solved."

    def describe_capabilities(self) -> str:
        """Returns a description of the agent's capabilities."""
        return "Mock agent capabilities."


class TestAgentRegistry(unittest.TestCase):
    """Unit tests for the AgentRegistry class."""

    @patch("agents.core.agent_registry.importlib.import_module")
    def setUp(self, mock_import_module):
        """Sets up a mocked agent registry for testing."""
        mock_module = MagicMock()
        mock_module.JournalAgent = MockAgent
        mock_module.TradingAgent = MockAgent
        mock_module.DebuggerAgent = MockAgent

        mock_import_module.side_effect = lambda module_path: mock_module

        self.registry = AgentRegistry()

    def test_load_agents(self):
        """Test if agents are correctly loaded into the registry."""
        self.assertIn("JournalAgent", self.registry.agents)
        self.assertIn("TradingAgent", self.registry.agents)
        self.assertIn("DebuggerAgent", self.registry.agents)

    def test_get_agent(self):
        """Test retrieving an agent by name."""
        agent = self.registry.get_agent("JournalAgent")
        self.assertIsInstance(agent, MockAgent)

    def test_list_agents(self):
        """Test listing registered agents."""
        agents_list = self.registry.list_agents()
        self.assertEqual(set(agents_list), {"JournalAgent", "TradingAgent", "DebuggerAgent"})


if __name__ == "__main__":
    unittest.main()
