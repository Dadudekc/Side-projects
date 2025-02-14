import logging
from typing import Dict, Any
from agents.core.utilities.AgentBase import AgentBase
from agents.core.utilities.ai_agent_utils import PerformanceMonitor, MemoryManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AgentActor(AgentBase):
    """
    Executes tasks and manages tool operations via ToolServer.
    """

    def __init__(self, tool_server, memory_manager: MemoryManager, performance_monitor: PerformanceMonitor):
        """
        Initializes AgentActor with tool server, memory, and performance monitoring.

        Args:
            tool_server: The ToolServer instance to manage tools.
            memory_manager: Instance for managing task memory.
            performance_monitor: Instance for tracking performance metrics.
        """
        super().__init__(name="AgentActor", project_name="AI_Agent_System")
        self.tool_server = tool_server
        self.memory_manager = memory_manager
        self.performance_monitor = performance_monitor
        logger.info("AgentActor initialized.")

    def describe_capabilities(self) -> str:
        """
        Returns a description of the agent's capabilities.
        """
        return "I execute Python scripts, shell commands, and interact with tools."

    def solve_task(self, task: str, **kwargs) -> Any:
        """
        Executes a given task (Python script, shell command, or tool operation).

        Args:
            task (str): The task type (e.g., "execute_python", "execute_shell", "use_tool").
            **kwargs: Additional parameters for task execution.

        Returns:
            Any: Result of the task execution.
        """
        logger.info(f"Executing task: {task} with parameters: {kwargs}")

        task_methods = {
            "execute_python": self._execute_python_task,
            "execute_shell": self._execute_shell_task,
            "use_tool": self.utilize_tool,
        }

        if task not in task_methods:
            error_msg = f"Error: Unsupported task type '{task}'"
            logger.error(error_msg)
            return error_msg

        return task_methods[task](**kwargs)

    def _execute_python_task(self, python_code: str) -> str:
        """Executes Python code."""
        try:
            result = self.tool_server.python_notebook.execute_code(python_code)
            return result
        except Exception as e:
            return f"Python execution failed: {str(e)}"

    def _execute_shell_task(self, command: str) -> str:
        """Executes shell command."""
        try:
            result = self.tool_server.shell.execute_command(command)
            return result
        except Exception as e:
            return f"Shell execution failed: {str(e)}"

    def utilize_tool(self, tool_name: str, operation: str, parameters: Dict[str, Any]) -> Any:
        """Uses a tool with specified parameters."""
        try:
            tool = getattr(self.tool_server, tool_name, None)
            if tool is None:
                return f"Tool '{tool_name}' not found"

            tool_method = getattr(tool, operation, None)
            if tool_method is None:
                return f"Operation '{operation}' not found in tool '{tool_name}'"

            return tool_method(**parameters)
        except Exception as e:
            return f"Failed to execute operation '{operation}' on tool '{tool_name}': {str(e)}"

    def shutdown(self) -> None:
        """Handles cleanup operations."""
        logger.info("AgentActor is shutting down.")
