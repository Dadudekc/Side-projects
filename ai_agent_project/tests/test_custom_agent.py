import unittest
import logging
from unittest.mock import patch
from agents.core.CustomAgent import CustomAgent

class TestCustomAgent(unittest.TestCase):
    """Unit tests for the CustomAgent class."""

    def setUp(self):
        """Set up a fresh instance of CustomAgent for each test."""
        self.agent = CustomAgent(project_name="AI_Debugger_Assistant")

    def test_initialization(self):
        """Test if the CustomAgent initializes correctly."""
        self.assertEqual(self.agent.name, "CustomAgent")
        self.assertEqual(self.agent.project_name, "AI_Debugger_Assistant")  # Fix: Match the actual default value

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
        result = self.agent.perform_task_logic("Test Logic Task", additional_info="Some info")
        self.assertIn("CustomAgent completed the task: Test Logic Task", result)

    def test_describe_capabilities(self):
        """Test the describe_capabilities method."""
        result = self.agent.describe_capabilities()
        self.assertIn("Handles custom-defined tasks with flexible execution logic.", result)

    def test_shutdown(self):
        """Test that shutdown logs properly."""
        with self.assertLogs(level="INFO") as log:
            self.agent.shutdown()
            self.assertTrue(any("CustomAgent is shutting down" in msg for msg in log.output))

if __name__ == "__main__":
    unittest.main()
