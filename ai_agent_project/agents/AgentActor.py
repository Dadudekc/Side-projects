import logging

class AgentActor:
    """
    Executes tasks and manages tool operations via ToolServer.
    """

    def __init__(self, tool_server, memory_manager, performance_monitor):
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
        logging.info("AgentActor initialized.")

    def describe_capabilities(self):
        """
        Returns a description of the agent's capabilities.
        """
        return "I execute Python scripts, shell commands, and interact with tools."

    def solve_task(self, task, **kwargs):
        """
        Executes a given task (Python script, shell command, or tool operation).

        Args:
            task (str): The task type (e.g., "execute_python", "execute_shell", "use_tool").
            **kwargs: Additional parameters for task execution.

        Returns:
            Any: Result of the task execution.
        """
        task_methods = {
            "execute_python": self._execute_python_task,
            "execute_shell": self._execute_shell_task,
            "use_tool": self.utilize_tool,
        }

        if task not in task_methods:
            return f"Error: Unsupported task type '{task}'"

        return task_methods[task](**kwargs)

    def _execute_python_task(self, python_code):
        """Executes Python code."""
        try:
            return self.tool_server.python_notebook.execute_code(python_code)
        except Exception as e:
            return f"Python execution failed: {str(e)}"

    def _execute_shell_task(self, command):
        """Executes shell command."""
        try:
            return self.tool_server.shell.execute_command(command)
        except Exception as e:
            return f"Shell execution failed: {str(e)}"

    def utilize_tool(self, tool_name, operation, parameters):
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

    def perform_task(self, task):
        """
        Executes a given task based on its type.

        Args:
            task (Dict[str, Any]): A dictionary containing task details.
        
        Returns:
            Any: Result of task execution.
        """
        task_type = task.get("type")
        if not task_type:
            return "Error: Task type is missing."

        if task_type == "python":
            return self._execute_python_task(task.get("content", ""))
        elif task_type == "shell":
            return self._execute_shell_task(task.get("content", ""))
        else:
            return f"Error: Unsupported task type '{task_type}'"

    def shutdown(self):
        """Handles cleanup operations."""
        logging.info("AgentActor is shutting down.")