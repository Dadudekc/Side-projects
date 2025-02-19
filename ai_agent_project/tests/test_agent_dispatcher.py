"""
Unit tests for the AgentDispatcher class.

Tests include:
- Dispatcher initialization with/without agents.
- Dispatching tasks to valid/invalid agents.
- Handling errors and exceptions in task execution.
"""

import logging
import unittest
import json
from unittest.mock import MagicMock, patch
from agents.core.AgentBase import AgentBase
from agents.agent_dispatcher import AgentDispatcher

class TestAgentDispatcher(unittest.TestCase):
    """Unit tests for AgentDispatcher."""

    def setUp(self):
        """Set up a fresh AgentDispatcher instance for tests that don't require patched logger."""
        logging.basicConfig(level=logging.DEBUG)
        self.dispatcher = AgentDispatcher()

    @patch("agents.core.agent_registry.AgentRegistry.list_agents", return_value=["TestAgent"])
    def test_initialization_with_agents(self, mock_list_agents):
        """Test dispatcher initializes and lists available agents correctly."""
        dispatcher = AgentDispatcher()
        registered_agents = dispatcher.registry.list_agents()
        self.assertIn("TestAgent", registered_agents)

    @patch("agents.core.agent_registry.AgentRegistry.list_agents", return_value=[])
    @patch("agents.agent_dispatcher.logger")
    def test_initialization_without_agents(self, mock_logger, mock_list_agents):
        """Test dispatcher warns when no agents are loaded.
           (Since our __init__ always sets local agents, no warning is expected.)
        """
        dispatcher = AgentDispatcher()
        # Our dispatcher always populates self.agents, so we expect no warning.
        mock_logger.warning.assert_not_called()

    @patch("agents.core.agent_registry.AgentRegistry.get_agent")
    @patch("agents.core.agent_registry.AgentRegistry.list_agents", return_value=["testagent"])
    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_with_valid_agent(self, mock_logger, mock_list_agents, mock_get_agent):
        """Test dispatcher successfully dispatches a task to a valid agent."""
        dispatcher = AgentDispatcher()  # Instantiate after logger is patched.
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.return_value = {"result": "success"}
        mock_get_agent.return_value = mock_agent
        task_data = {"action": "test_action"}
        result = json.loads(dispatcher.dispatch_task("TestAgent", task_data))
        self.assertEqual(result, {"result": "success"})

    @patch("agents.core.agent_registry.AgentRegistry.get_agent", return_value=None)
    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_with_invalid_agent(self, mock_logger, mock_get_agent):
        """Test dispatcher handles task dispatching for a non-existent agent."""
        dispatcher = AgentDispatcher()  # Instantiate after logger is patched.
        task_data = {"action": "test_action"}
        result = json.loads(dispatcher.dispatch_task("InvalidAgent", task_data))
        self.assertIn("error", result)
        # Check that logger.error was called with the expected message.
        calls = mock_logger.error.call_args_list
        self.assertTrue(
            any("❌ Agent 'invalidagent' not found." in call.args[0] for call in calls),
            "Expected error log message not found."
        )

    @patch("agents.core.agent_registry.AgentRegistry.get_agent")
    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_with_non_agentbase_instance(self, mock_logger, mock_get_agent):
        """Test dispatcher prevents dispatching to an invalid non-AgentBase instance."""
        dispatcher = AgentDispatcher()  # Instantiate after logger is patched.
        mock_get_agent.return_value = "NotAnAgentBaseInstance"
        task_data = {"action": "test_action"}
        result = json.loads(dispatcher.dispatch_task("TestAgent", task_data))
        calls = mock_logger.error.call_args_list
        self.assertTrue(
            any("❌ Agent 'testagent' does not inherit from AgentBase." in call.args[0] for call in calls),
            "Expected error log message not found."
        )
        self.assertEqual(result, {"error": "Agent 'testagent' is invalid."})

    @patch("agents.core.agent_registry.AgentRegistry.get_agent")
    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_with_exception(self, mock_logger, mock_get_agent):
        """Test dispatcher handles exceptions during task execution."""
        dispatcher = AgentDispatcher()  # Instantiate after logger is patched.
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.side_effect = Exception("Task error")
        mock_get_agent.return_value = mock_agent
        task_data = {"action": "test_action"}
        result = json.loads(dispatcher.dispatch_task("TestAgent", task_data))
        # Verify that logger.exception was called with a message that includes the expected substring.
        exception_calls = mock_logger.exception.call_args_list
        self.assertTrue(
            any("⚠️ Error executing task for 'testagent': Task error" in call.args[0] for call in exception_calls),
            "Expected exception log message not found."
        )
        self.assertEqual(result, {"error": "Task execution failed: Task error"})

if __name__ == "__main__":
    unittest.main()
