import unittest
from unittest.mock import patch, MagicMock
from agents.core.utilities.AgentBase import (
    AgentBase,
    AIModelManager,
    AIPatchUtils,
    CustomAgent,
    DeepSeekModel,
    MistralModel,
    OpenAIModel,
)


class MockAgent(AgentBase):
    """Mock implementation of AgentBase for testing purposes."""

    def solve_task(self, task: str, **kwargs):
        return f"Task '{task}' solved."

    def describe_capabilities(self) -> str:
        return "Mock agent capabilities."


class TestAgentRegistry(unittest.TestCase):
    """Unit tests for the AgentRegistry class."""

    @patch("agents.core.AgentRegistry.importlib.import_module")
    def setUp(self, mock_import_module):
        """Setup method to mock agent loading."""
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
        self.assertEqual(
            set(agents_list), {"JournalAgent", "TradingAgent", "DebuggerAgent"}
        )


if __name__ == "__main__":
    unittest.main()
