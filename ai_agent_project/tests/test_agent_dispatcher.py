"""
Unit tests for the AgentDispatcher class.

Tests include:
- Dispatcher initialization with/without agents.
- Dispatching tasks to valid/invalid agents.
- Handling errors and exceptions in task execution.
- Dispatching tasks to internal dummy agents.
- Dispatching tasks to external agents via adapters.
"""

import json
import logging
import unittest
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

# Define an agent that simulates missing task handling by always raising an AttributeError.
class InvalidAgent(DummyAgent):
    def solve_task(self, action: str, **kwargs):
        raise AttributeError("Agent does not implement a task handling method.")

# Concrete subclass of ExternalAIAdapter for testing.
class ExternalAIAdapterMock(ExternalAIAdapter):
    def __init__(self, api_key: str, endpoint: str):
        super().__init__(api_key, endpoint)

    def describe_capabilities(self) -> str:
        return "Mock external AI capabilities"

    def solve_task(self, action: str, **kwargs) -> dict:
        import requests
        response = requests.post(self.endpoint, json={"action": action, **kwargs})
        return response.json()

# Custom dispatcher subclass to simulate an empty registry.
class EmptyAgentDispatcher(AgentDispatcher):
    def __init__(self):
        # Skip auto-discovery and manual registration.
        self.registry = None
        self.agents = {}
        # Use the module-level logger.
        logger = logging.getLogger("agents.agent_dispatcher")
        logger.info("✅ AgentDispatcher initialized.")
        if not self.agents:
            logger.warning("⚠️ No agents were loaded into the registry!")

class TestAgentDispatcher(unittest.TestCase):
    """Unit tests for AgentDispatcher."""

    def setUp(self):
        # Patch out auto-discovery so that unwanted agents are not registered.
        with patch.object(AgentDispatcher, "_discover_agents", return_value=None):
            self.dispatcher = AgentDispatcher()
        self.dispatcher.agents = {}  # Start with a controlled, empty registry.

    def test_initialization_with_agents(self):
        """Test dispatcher initializes and lists available agents correctly."""
        self.dispatcher.agents = {"testagent": DummyAgent()}
        registered_agents = list(self.dispatcher.agents.keys())
        self.assertIn("testagent", registered_agents)

    def test_initialization_without_agents(self):
        """Test dispatcher warns when no agents are loaded."""
        with self.assertLogs("agents.agent_dispatcher", level="WARNING") as cm:
            EmptyAgentDispatcher()
        # Assert that one of the logged messages contains the expected warning.
        self.assertTrue(any("⚠️ No agents were loaded into the registry!" in message for message in cm.output))

    def test_register_agent_valid(self):
        """Test registering a valid agent."""
        agent = DummyAgent()
        self.dispatcher.register_agent("dummy", agent)
        self.assertIn("dummy", self.dispatcher.agents)
        self.assertIsInstance(self.dispatcher.agents["dummy"], DummyAgent)

    def test_register_agent_invalid(self):
        """Test attempting to register an invalid agent."""
        with self.assertLogs("agents.agent_dispatcher", level="ERROR") as cm:
            self.dispatcher.register_agent("invalid", "NotAnAgentBaseInstance")
        self.assertTrue(any("Agent 'invalid' does not inherit from AgentBase." in message for message in cm.output))

    def test_register_duplicate_agent(self):
        """Test registering an agent that already exists."""
        self.dispatcher.register_agent("dummy", DummyAgent())
        with self.assertLogs("agents.agent_dispatcher", level="WARNING") as cm:
            self.dispatcher.register_agent("dummy", DummyAgent())
        self.assertTrue(any("Agent 'dummy' is already registered." in message for message in cm.output))

    def test_dispatch_task_valid_agent(self):
        """Test dispatcher successfully dispatches a task to a valid agent."""
        agent = DummyAgent()
        self.dispatcher.register_agent("dummy", agent)
        task_data = {"action": "test_action"}
        result = json.loads(self.dispatcher.dispatch_task("dummy", task_data))
        self.assertEqual(result, {"status": "success", "message": "Dummy agent processed test_action"})

    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_invalid_agent(self, mock_logger):
        """Test dispatcher handles task dispatching for a non-existent agent."""
        task_data = {"action": "test_action"}
        result = json.loads(self.dispatcher.dispatch_task("invalid", task_data))
        self.assertIn("Agent 'invalid' not found.", mock_logger.error.call_args[0][0])
        self.assertEqual(result, {"error": "Agent 'invalid' not found."})

    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_agent_without_methods(self, mock_logger):
        """
        Test dispatcher handles an agent missing task handling methods.
        We simulate this by registering an InvalidAgent whose solve_task method
        always raises an AttributeError.
        """
        self.dispatcher.register_agent("invalid_agent", InvalidAgent())
        task_data = {"action": "test_action"}
        result = json.loads(self.dispatcher.dispatch_task("invalid_agent", task_data))
        # Assert that an exception was logged.
        self.assertTrue(any("Agent does not implement a task handling method." in call.args[0] for call in mock_logger.exception.call_args_list))
        self.assertIn("Task execution failed", result["error"])

    @patch("agents.agent_dispatcher.logger")
    def test_dispatch_task_exception_handling(self, mock_logger):
        """Test dispatcher handles exceptions in task execution."""
        mock_agent = MagicMock(spec=AgentBase)
        mock_agent.solve_task.side_effect = Exception("Unexpected Error")
        self.dispatcher.agents["dummy"] = mock_agent
        task_data = {"action": "test_action"}
        result = json.loads(self.dispatcher.dispatch_task("dummy", task_data))
        self.assertTrue(any("Error executing task" in call.args[0] for call in mock_logger.exception.call_args_list))
        self.assertEqual(result, {"error": "Task execution failed: Unexpected Error"})

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
