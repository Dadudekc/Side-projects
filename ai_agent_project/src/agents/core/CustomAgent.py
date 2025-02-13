# File Path: C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\agents\core\CustomAgent.py

import logging
from typing import Any, Dict, Optional
from ai_agent_project.src.agents.core.utilities.agent_base import AgentBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class CustomAgent(AgentBase):
    """
    CustomAgent Class

    This class provides a customizable agent with flexible task-solving capabilities.
    It can handle user-defined tasks with an extensible architecture, inheriting from the
    base `AgentBase` class.
    """

    def __init__(self, name: str = "CustomAgent", project_name: str = "AI_Debugger_Assistant"):
        """
        Initializes the CustomAgent, setting up logging and required resources.

        Args:
            name (str): Name of the agent (default is "CustomAgent").
            project_name (str): Project or domain the agent is associated with.
        """
        super().__init__(name=name, project_name=project_name)
        logger.info(f"{self.name} initialized for project '{self.project_name}'.")

    def solve_task(self, task: str, **kwargs) -> Any:
        """
        Executes a custom-defined task, handling errors gracefully.

        Args:
            task (str): The main task description.
            **kwargs: Additional arguments required for task execution.

        Returns:
            Any: Result of the executed task or error message if task fails.
        """
        logger.info(f"{self.name} is starting task execution: '{task}'")
        try:
            # Placeholder for actual task logic
            result = self.perform_task_logic(task, **kwargs)
            logger.info(f"Task '{task}' executed successfully.")
            return result
        except Exception as e:
            logger.error(f"Error executing task '{task}': {e}", exc_info=True)
            return f"Error executing task: {e}"

    def perform_task_logic(self, task: str, **kwargs) -> str:
        """
        Implements the core logic for task execution.

        Args:
            task (str): Description of the task.
            **kwargs: Additional parameters for task-specific logic.

        Returns:
            str: Message indicating task completion.
        """
        # Example of using task data and handling kwargs
        additional_info = kwargs.get("additional_info", "No additional info provided.")
        logger.debug(f"Performing task with details: {task}, Additional Info: {additional_info}")
        
        # Simulate task completion with custom message
        return f"{self.name} completed the task: {task}. Details: {additional_info}"

    def describe_capabilities(self) -> str:
        """
        Provides a description of the agent’s capabilities.

        Returns:
            str: Description of what the agent can do.
        """
        capabilities = "Handles custom-defined tasks with flexible execution logic."
        logger.debug(f"{self.name} capabilities: {capabilities}")
        return capabilities

    def shutdown(self) -> None:
        """
        Shuts down the agent, releasing any allocated resources.
        """
        logger.info(f"{self.name} is shutting down and releasing resources.")
        # Add any resource cleanup logic if needed
