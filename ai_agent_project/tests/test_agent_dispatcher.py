"""
Unit tests for the AgentDispatcher class.

Tests include:
- Dispatcher initialization with/without agents.
- Dispatching tasks to valid/invalid agents.
- Handling errors and exceptions in task execution.
- Dispatching tasks to internal dummy agents.
- Dispatching tasks to external agents via adapters.
"""

import pytest
import logging
import unittest
import json
from unittest.mock import MagicMock, patch
from agents.core.AgentBase import AgentBase
from agents.agent_dispatcher import AgentDispatcher
from agents.external_ai_agent import ExternalAIAdapter

# Create a dummy AgentBase subclass for testing.
class DummyAgent(AgentBase):
    def __init__(self, name="dummy", project_name="test_project"):
        super().__init__(name, project_name)

    def describe_capabilities(self) -> str:
        return "Dummy capabilities"

    def solve_task(self, action: str, **kwargs) -> dict:
        return {"status": "success", "message": f"Dummy agent processed {action}"}


# Concrete subclass of ExternalAIAdapter for testing
class ExternalAIAdapterMock(ExternalAIAdapter):
    def __init__(self, api_key: str, endpoint: str):
        super().__init__(api_key, endpoint)

    def describe_capabilities(self) -> str:
        return "Mock external AI capabilities"

    def solve_task(self, action: str, **kwargs) -> dict:
        import requests  # Ensure requests is explicitly used
        response = requests.post(self.endpoint, json={"action": action, **kwargs})
        return response.json()


class TestAgentDispatcher(unittest.TestCase):
    """Unit tests for AgentDispatcher."""

    def setUp(self):
        """Set up a fresh AgentDispatcher instance for tests."""
        logging.basicConfig(level=logging.DEBUG)
        self.dispatcher = AgentDispatcher()
        self.dispatcher.agents = {}  # Clear discovered agents

    def test_initialization_with_agents(self):
        """Test dispatcher initializes and lists available agents correctly."""
        self.dispatcher.agents = {"testagent": DummyAgent()}
        registered_agents = list(self.dispatcher.agents.keys())
        self.assertIn("testagent", registered_agents)

    @patch("agents.agent_dispatcher.logger")
    def test_initialization_without_agents(self, mock_logger):
        """Test dispatcher warns when no agents are loaded."""
        with patch.object(AgentDispatcher, "_discover_agents", return_value=None):
            dispatcher = AgentDispatcher()
            dispatcher.agents = {}  # Force empty agents registry
            if not dispatcher.agents:
                mock_logger.warning.assert_called_with("⚠️ No agents were loaded into the registry!")

    def test_dispatch_task_with_valid_agent(self):
        """Test dispatcher successfully dispatches a task to a valid agent."""
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.return_value = {"result": "success"}
        self.dispatcher.agents["testagent"] = mock_agent
        task_data = {"action": "test_action"}
        result = json.loads(self.dispatcher.dispatch_task("TestAgent", task_data))
        self.assertEqual(result, {"result": "success"})

    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_with_invalid_agent(self, mock_logger):
        """Test dispatcher handles task dispatching for a non-existent agent."""
        task_data = {"action": "test_action"}
        result = json.loads(self.dispatcher.dispatch_task("InvalidAgent", task_data))
        self.assertIn("error", result)
        calls = mock_logger.error.call_args_list
        self.assertTrue(any("❌ Agent 'invalidagent' not found." in call.args[0] for call in calls))

    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_with_non_agentbase_instance(self, mock_logger):
        """Test dispatcher prevents dispatching to an invalid non-AgentBase instance."""
        self.dispatcher.agents["testagent"] = "NotAnAgentBaseInstance"
        task_data = {"action": "test_action"}
        result = json.loads(self.dispatcher.dispatch_task("TestAgent", task_data))

        calls = mock_logger.error.call_args_list
        self.assertTrue(
            any("❌ Agent 'testagent' does not inherit from AgentBase." in call.args[0] for call in calls),
            "Expected error log message not found."
        )
        self.assertEqual(result, {"error": "Agent 'testagent' is invalid."})


    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_with_exception(self, mock_logger):
        """Test dispatcher handles exceptions during task execution."""
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.side_effect = Exception("Task error")
        self.dispatcher.agents["testagent"] = mock_agent
        task_data = {"action": "test_action"}
        result = json.loads(self.dispatcher.dispatch_task("TestAgent", task_data))

        exception_calls = mock_logger.exception.call_args_list
        self.assertTrue(any("⚠️ Error executing task for 'testagent': Task error" in call.args[0] for call in exception_calls))
        self.assertEqual(result, {"error": "Task execution failed: Task error"})

    def test_dispatch_internal_agent(self):
        """Test dispatching a task to an internal dummy agent."""
        self.dispatcher.register_agent("dummy", DummyAgent())
        task = {"action": "test_action", "param": "value"}
        response = self.dispatcher.dispatch_task("dummy", task)
        response_data = json.loads(response)
        self.assertEqual(response_data.get("status"), "success")
        self.assertIn("Dummy agent processed", response_data.get("message"))

    @patch("requests.post")
    def test_dispatch_external_agent(self, mock_post):
        """Test dispatching a task to an external agent adapter."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status": "success", "result": "External result"}
        mock_post.return_value = mock_response

        external_agent = ExternalAIAdapterMock(api_key="fake_key", endpoint="http://fake-endpoint.com")
        self.dispatcher.register_agent("external", external_agent)

        task = {"action": "analyze", "text": "Some text"}
        response = self.dispatcher.dispatch_task("external", task)
        response_data = json.loads(response)

        self.assertEqual(response_data.get("status"), "success")
        self.assertEqual(response_data.get("result"), "External result")

        mock_post.assert_called_once_with("http://fake-endpoint.com", json={"action": "analyze", "text": "Some text"})

    def test_dispatch_invalid_agent(self):
        """Test dispatching a task to a non-existent agent."""
        response = self.dispatcher.dispatch_task("nonexistent", {"action": "test"})
        response_data = json.loads(response)
        self.assertIn("error", response_data)
        self.assertIn("not found", response_data["error"])


if __name__ == "__main__":
    unittest.main()
