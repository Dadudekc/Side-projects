"""
Module for unit testing the functionality of AgentDispatcher class.

This module includes setup for initializing an instance of AgentDispatcher class 
and tests for dispatching tasks to valid agents.

Classes:
    TestAgentDispatcher: A unit test class for testing AgentDispatcher class.

Functions:
    setUp(self): Initialize an AgentDispatcher instance before each test.
    test_dispatch_valid_agent(self): Test dispatching a tasks to a valid agent and correct processing.  

Raises:
    AssertionError: An error occurred when the dispatched task
"""

import json
import unittest

from agents.AgentDispatcher import AgentDispatcher
from agents.core.AgentBase import AgentBase
from agents.core.utilities.ai_patch_utils import AIPatchUtils
from agents.custom_agent import CustomAgent
from ai_engine.models.ai_model_manager import AIModelManager
from ai_engine.models.deepseek_model import DeepSeekModel
from ai_engine.models.mistral_model import MistralModel
from ai_engine.models.openai_model import OpenAIModel


class TestAgentDispatcher(unittest.TestCase):
    """Unit tests for AgentDispatcher."""

    def setUp(self):
        """Initialize the agent dispatcher before each test."""
        self.dispatcher = AgentDispatcher()

    def test_dispatch_valid_agent(self):
        """Test dispatching a task to a valid agent."""
        task_data = {
            "action": "create",
            "title": "Test Journal",
            "content": "Test content",
        }

        # Get the response from the dispatcher
        result = self.dispatcher.dispatch_task("JournalAgent", task_data)

        # Ensure result is a string (since we convert dicts to JSON strings)
        self.assertIsInstance(result, str)

        # Convert result to a dictionary
        try:
            result_data = json.loads(result)
        except json.JSONDecodeError:
            self.fail("AgentDispatcher did not return a valid JSON string.")

        # Ensure status is "success"
        self.assertEqual(
            result_data.get("status"),
            "success",
            "JournalAgent did not process the task correctly.",
        )


if __name__ == "__main__":
    unittest.main()
