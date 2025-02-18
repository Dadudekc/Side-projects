"""

A unit test class for the AgentActor class (from agents.AgentActor) in an AI framework. 

The test cases in this class cover the behavior of the AgentActor, which mainly includes 
describing its capabilities, executing Python scripts, executing shell commands, interacting 
with various tools, performing various tasks, and shutting down the AgentActor.

Entities Mocked:
- self.tool_server: a mock object that simulates the behavior of a server running various tools.
- self.memory_manager: a
"""

import unittest
from unittest.mock import MagicMock

from ai_engine.models.memory.memory_manager import MemoryManager
from ai_engine.models.memory.vector_memory_manager import VectorMemoryManager
from agents.AgentActor import AgentActor
from agents.core.utilities.ai_agent_utils import PerformanceMonitor


class TestAgentActor(unittest.TestCase):
    def setUp(self):
        self.tool_server = MagicMock()
        # Use the updated VectorMemoryManager without latent_dim
        dummy_embedding_model = MagicMock()
        # Simulate the encode() method: return the UTF-8 byte values of the input string as a float array.
        dummy_embedding_model.encode.side_effect = lambda text: [float(ord(c)) for c in text]
        
        self.memory_manager = VectorMemoryManager(memory_limit=50, embedding_model=dummy_embedding_model)
        self.performance_monitor = PerformanceMonitor()
        self.agent = AgentActor(self.tool_server, self.memory_manager, self.performance_monitor)

    def test_describe_capabilities(self):
        self.assertEqual(
            self.agent.describe_capabilities(),
            "I execute Python scripts, shell commands, and interact with tools.",
        )

    def test_solve_task_execute_python(self):
        self.tool_server.python_notebook.execute_code.return_value = "Python Execution Successful"
        result = self.agent.solve_task("execute_python", python_code="print('Hello')")
        self.assertEqual(result, "Python Execution Successful")

    def test_solve_task_execute_shell(self):
        self.tool_server.shell.execute_command.return_value = "Shell Execution Successful"
        result = self.agent.solve_task("execute_shell", command="ls")
        self.assertEqual(result, "Shell Execution Successful")

    def test_solve_task_invalid(self):
        result = self.agent.solve_task("invalid_task")
        self.assertEqual(result, "Error: Unsupported task type 'invalid_task'")

    def test_utilize_tool_valid(self):
        mock_tool = MagicMock()
        mock_tool.some_operation.return_value = "Operation Successful"
        setattr(self.tool_server, "mock_tool", mock_tool)

        result = self.agent.utilize_tool("mock_tool", "some_operation", {})
        self.assertEqual(result, "Operation Successful")

    def test_utilize_tool_invalid_tool(self):
        self.tool_server.unknown_tool = None  # Ensure tool does not exist
        result = self.agent.utilize_tool("unknown_tool", "operation", {})
        self.assertEqual(result, "Tool 'unknown_tool' not found")


    def test_utilize_tool_invalid_operation(self):
        mock_tool = MagicMock()
        setattr(self.tool_server, "mock_tool", mock_tool)

        # Ensure the tool does not have the operation
        delattr(mock_tool, "unknown_operation")  # Prevents MagicMock from creating it dynamically

        result = self.agent.utilize_tool("mock_tool", "unknown_operation", {})
        
        self.assertEqual(result, "Operation 'unknown_operation' not found in tool 'mock_tool'")


        result = self.agent.utilize_tool("mock_tool", "unknown_operation", {})
        self.assertEqual(result, "Operation 'unknown_operation' not found in tool 'mock_tool'")

    def test_perform_task_python(self):
        self.tool_server.python_notebook.execute_code.return_value = "Python Execution Successful"
        result = self.agent.perform_task({"type": "python", "content": "print('Hello')"})
        self.assertEqual(result, "Python Execution Successful")

    def test_perform_task_shell(self):
        self.tool_server.shell.execute_command.return_value = "Shell Execution Successful"
        result = self.agent.perform_task({"type": "shell", "content": "ls"})
        self.assertEqual(result, "Shell Execution Successful")

    def test_perform_task_invalid_type(self):
        result = self.agent.perform_task({"type": "invalid"})
        self.assertEqual(result, "Error: Unsupported task type 'invalid'")

    def test_shutdown(self):
        with self.assertLogs(level="INFO") as log:
            self.agent.shutdown()
        self.assertIn("AgentActor is shutting down.", log.output[0])


if __name__ == "__main__":
    unittest.main()
