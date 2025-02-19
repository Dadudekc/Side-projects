"""
The `AgentBase` class is an abstract base class that forms the foundation for all AI agents. 
It dictates the structure and shared methods for logging, task execution, and lifecycle management. 
All subclasses must implement the abstract `solve_task` and `describe_capabilities` methods.

Methods:
- `__init__(self, name: str, project_name: str)`: Initializes the agent with a name and project association.
- `solve_task(self, task: str, **kwargs)`: Abstract method for executing tasks.
- `describe_capabilities(self) -> str`: Abstract method for describing the agent’s functions.
- `shutdown(self) -> None`: Logs shutdown information and performs cleanup if necessary.
"""

from typing import Dict, Any
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AgentBase(ABC):
    """
    Abstract Base Class for AI Agents.

    Provides a foundation for all AI agents, enforcing structure and
    shared methods for logging, task execution, and lifecycle management.
    """

    def __init__(self, name: str, project_name: str):
        """
        Initializes the base agent with a name and project association.

        Args:
            name (str): The name of the agent.
            project_name (str): The project this agent belongs to.
        """
        self.name = name
        self.project_name = project_name
        logger.info(f"✅ Agent '{self.name}' initialized for project '{self.project_name}'.")

    @abstractmethod
    def solve_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Abstract method for task execution.
        Must be implemented by all subclasses.

        Args:
            task (str): The task description.
            **kwargs: Additional parameters for task execution.

        Returns:
            Dict[str, Any]: A dictionary containing the task result.
        """
        pass

    @abstractmethod
    def describe_capabilities(self) -> str:
        """
        Provides a description of the agent's capabilities.
        Must be overridden by all subclasses.

        Returns:
            str: A description of the agent's functionalities.
        """
        pass

    def shutdown(self) -> None:
        """
        Logs a shutdown message, ensuring graceful cleanup.
        Can be overridden in subclasses if additional cleanup is needed.
        """
        logger.info(f"⚠️ Shutting down agent '{self.name}' from project '{self.project_name}'.")
