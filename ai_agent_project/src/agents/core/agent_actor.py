import subprocess
import logging
from typing import List, Dict, Any, Optional
from utilities.ai_agent_utils import PerformanceMonitor, MemoryManager

logger = logging.getLogger(__name__)

class AgentActor:
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
        self.tool_server = tool_server
        self.memory_manager = memory_manager
        self.performance_monitor = performance_monitor
        logger.info("AgentActor initialized without Docker dependency.")

    def solve_task(self, task: str) -> str:
        """
        Executes a given task as either Python code or shell command.
        
        Args:
            task (str): The task to execute. Prefix 'python:' for Python code execution.

        Returns:
            str: Result of the task execution.
        """
        logger.info(f"Received task: {task}")

        # Determine task type and route to the correct executor
        if task.startswith("python:"):
            # Execute Python code
            python_code = task[len("python:"):].strip()
            result = self._execute_python_task(python_code)
        else:
            # Execute as shell command
            result = self._execute_shell_task(task)
        
        # Log and return result
        logger.debug(f"Task result: {result}")
        return result

    def _execute_python_task(self, python_code: str) -> str:
        """
        Executes Python code within the PythonNotebook environment.
        
        Args:
            python_code (str): The Python code to execute.

        Returns:
            str: Result or error message from Python execution.
        """
        try:
            result = self.tool_server.python_notebook.execute_code(python_code)
            logger.info("Executed Python code successfully.")
            return result
        except Exception as e:
            error_msg = f"Python task execution failed: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _execute_shell_task(self, command: str) -> str:
        """
        Executes a shell command using the ToolServer's shell tool.
        
        Args:
            command (str): The shell command to execute.

        Returns:
            str: Command output or error message.
        """
        try:
            result = self.tool_server.shell.execute_command(command)
            logger.info("Executed shell command successfully.")
            return result
        except Exception as e:
            error_msg = f"Shell task execution failed: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def utilize_tool(self, tool_name: str, operation: str, parameters: Dict[str, Any]) -> Any:
        """
        Executes an operation on a specified tool within ToolServer.
        
        Args:
            tool_name (str): Name of the tool in ToolServer.
            operation (str): The operation method to call on the tool.
            parameters (Dict[str, Any]): Dictionary of parameters for the operation.

        Returns:
            Any: Result of the tool operation or error message.
        """
        try:
            tool = getattr(self.tool_server, tool_name)
            tool_method = getattr(tool, operation)
            result = tool_method(**parameters)
            logger.info(f"Operation '{operation}' on tool '{tool_name}' completed successfully.")
            return result
        except AttributeError:
            error_msg = f"Tool '{tool_name}' or operation '{operation}' not found in ToolServer."
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Failed to execute operation '{operation}' on tool '{tool_name}': {str(e)}"
            logger.error(error_msg)
            return error_msg
