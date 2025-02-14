import unittest
from unittest.mock import MagicMock, patch
from agents.core.AgentActor import AgentActor

class TestAgentActor(unittest.TestCase):
    """Unit tests for AgentActor class."""

    def setUp(self):
        """Set up mock dependencies before each test."""
        self.mock_tool_server = MagicMock()
        self.mock_memory_manager = MagicMock()
        self.mock_performance_monitor = MagicMock()
        self.agent = AgentActor(self.mock_tool_server, self.mock_memory_manager, self.mock_performance_monitor)

    def test_perform_task_python_execution(self):
        """Test Python task execution via ToolServer."""
        self.mock_tool_server.python_notebook.execute_code.return_value = "Python execution success."
        task_data = {"type": "python", "content": "print('Hello')"}
        result = self.agent.perform_task(task_data)
        self.assertEqual(result, "Python execution success.")

    def test_perform_task_python_execution_error(self):
        """Test handling of Python execution errors."""
        self.mock_tool_server.python_notebook.execute_code.side_effect = Exception("Python error")
        task_data = {"type": "python", "content": "print('Hello')"}
        result = self.agent.perform_task(task_data)
        self.assertIn("Python execution failed", result)

    def test_perform_task_shell_execution(self):
        """Test shell command execution via ToolServer."""
        self.mock_tool_server.shell.execute_command.return_value = "Shell execution success."
        task_data = {"type": "shell", "content": "echo Hello"}
        result = self.agent.perform_task(task_data)
        self.assertEqual(result, "Shell execution success.")

    def test_perform_task_shell_execution_error(self):
        """Test handling of shell execution errors."""
        self.mock_tool_server.shell.execute_command.side_effect = Exception("Shell error")
        task_data = {"type": "shell", "content": "echo Hello"}
        result = self.agent.perform_task(task_data)
        self.assertIn("Shell execution failed", result)

if __name__ == "__main__":
    unittest.main()
