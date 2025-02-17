import logging
import unittest
from unittest.mock import MagicMock, patch

from agents.core.AgentBase import AgentBase
from agents.core.utilities.ai_model_manager import AIModelManager
from agents.core.utilities.ai_patch_utils import AIPatchUtils
from agents.core.utilities.CustomAgent import CustomAgent
from agents.AgentDispatcher import AgentDispatcher
from agents.core.agent_registry import AgentRegistry
from ai_engine.models.deepseek_model import DeepSeekModel
from ai_engine.models.mistral_model import MistralModel
from ai_engine.models.openai_model import OpenAIModel
class TestAgentDispatcher(unittest.TestCase):
    """Unit tests for AgentDispatcher."""

    @patch("agents.agent_registry.AgentRegistry.list_agents", return_value=["TestAgent"])
    def test_initialization_with_agents(self, mock_list_agents):
        """Test dispatcher initializes with agents."""
        dispatcher = AgentDispatcher()
        self.assertEqual(dispatcher.agents, ["TestAgent"])

    @patch("agents.agent_registry.AgentRegistry.list_agents", return_value=[])
    @patch("logging.warning")
    def test_initialization_without_agents(self, mock_warning, mock_list_agents):
        """Test dispatcher warns when no agents are loaded."""
        dispatcher = AgentDispatcher()
        mock_warning.assert_called_with("No agents were loaded into the registry!")

    @patch("agents.agent_registry.AgentRegistry.get_agent")
    def test_dispatch_task_with_valid_agent(self, mock_get_agent):
        """Test dispatcher successfully dispatches task to a valid agent."""
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.return_value = {"result": "success"}
        mock_get_agent.return_value = mock_agent

        dispatcher = AgentDispatcher()
        task_data = {"action": "test_action"}
        result = dispatcher.dispatch_task("TestAgent", task_data)

        self.assertEqual(result, {"result": "success"})

    @patch("agents.agent_registry.AgentRegistry.get_agent", return_value=None)
    @patch("logging.error")
    def test_dispatch_task_with_invalid_agent(self, mock_error, mock_get_agent):
        """Test dispatcher handles task dispatching for a non-existent agent."""
        dispatcher = AgentDispatcher()
        task_data = {"action": "test_action"}
        result = dispatcher.dispatch_task("InvalidAgent", task_data)

        mock_error.assert_called_with("Agent 'InvalidAgent' not found in registry.")
        self.assertEqual(result, {"error": "Agent 'InvalidAgent' not found."})

    @patch("agents.agent_registry.AgentRegistry.get_agent")
    @patch("logging.error")
    def test_dispatch_task_with_non_agentbase_instance(self, mock_error, mock_get_agent):
        """Test dispatcher prevents dispatching to an invalid non-AgentBase instance."""
        mock_get_agent.return_value = "NotAnAgentBaseInstance"
        dispatcher = AgentDispatcher()
        task_data = {"action": "test_action"}
        result = dispatcher.dispatch_task("TestAgent", task_data)

        mock_error.assert_called_with("Agent 'TestAgent' does not inherit from AgentBase.")
        self.assertEqual(result, {"error": "Agent 'TestAgent' is invalid."})

    @patch("agents.agent_registry.AgentRegistry.get_agent")
    @patch("logging.error")
    def test_dispatch_task_with_exception(self, mock_error, mock_get_agent):
        """Test dispatcher handles exceptions during task execution."""
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.side_effect = Exception("Task error")
        mock_get_agent.return_value = mock_agent

        dispatcher = AgentDispatcher()
        task_data = {"action": "test_action"}
        result = dispatcher.dispatch_task("TestAgent", task_data)

        mock_error.assert_called_with("Error executing task for 'TestAgent': Task error")
        self.assertEqual(result, {"error": "Task execution failed: Task error"})


if __name__ == "__main__":
    unittest.main()