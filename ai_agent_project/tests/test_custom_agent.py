"""

This Python module is a unit test for the CustomAgent class. It includes tests for initialization, describing capabilities, solving tasks in both success and failure scenarios, performing task logic, and shutdown.

The tests are performed via unittest framework. In cases a method is expected to fail, it uses mocking strategy via unittest.mock to simulate errors and check how method is handling them.

Note: This unit test requires AgentBase, AIModelManager, AIPatchUtils, CustomAgent from the agents.core package,
"""

import logging
import unittest
from unittest.mock import patch

from agents.core.AgentBase import AgentBase
from agents.core.utilities.ai_model_manager import AIModelManager
from agents.core.utilities.ai_patch_utils import AIPatchUtils
from agents.core.utilities.CustomAgent import CustomAgent
from ai_engine.models.deepseek_model import DeepSeekModel
from ai_engine.models.mistral_model import MistralModel
from ai_engine.models.openai_model import OpenAIModel

class TestCustomAgent(unittest.TestCase):
    """Unit tests for the CustomAgent class."""

    def setUp(self):
        """Set up a fresh instance of CustomAgent for each test."""
        self.agent = CustomAgent(project_name="AI_Debugger_Assistant")

    def test_initialization(self):
        """Test if the CustomAgent initializes correctly."""
        self.assertEqual(self.agent.name, "CustomAgent")
        self.assertEqual(self.agent.project_name, "AI_Debugger_Assistant")

    def test_describe_capabilities(self):
        """Test the describe_capabilities method."""
        self.assertEqual(
            self.agent.describe_capabilities(),
            "Handles custom-defined tasks with flexible execution logic."
        )

    def test_solve_task_success(self):
        """Test the solve_task method with valid task execution."""
        result = self.agent.solve_task("Test Task", additional_info="Extra data")
        self.assertIn("CustomAgent completed the task: Test Task", result)

    @patch.object(CustomAgent, "perform_task_logic", side_effect=ValueError("Simulated error."))
    def test_solve_task_with_error(self, mock_task_logic):
        """Test handling of exceptions in solve_task."""
        result = self.agent.solve_task("Failing Task")
        self.assertIn("Error executing task", result)

    def test_perform_task_logic(self):
        """Test perform_task_logic returns expected result."""
        result = self.agent.perform_task_logic("Sample Task", additional_info="Some info")
        self.assertEqual(result, "CustomAgent completed the task: Sample Task. Details: Some info")

    def test_solve_task_failure(self):
        """Test solve_task method handling a task failure."""
        def faulty_logic(*args, **kwargs):
            raise ValueError("Intentional error")

        self.agent.perform_task_logic = faulty_logic
        result = self.agent.solve_task("Faulty Task")
        self.assertIn("Error executing task", result)

    def test_shutdown(self):
        """Test that shutdown logs properly."""
        with self.assertLogs(level="INFO") as log:
            self.agent.shutdown()
        self.assertTrue(any("CustomAgent is shutting down" in msg for msg in log.output))


if __name__ == "__main__":
    unittest.main()
