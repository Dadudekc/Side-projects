# Path: ai_agent_project/src/plugins/plugin_interface.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class AgentPlugin(ABC):
    """
    Abstract base class for all agent plugins.
    """

    def __init__(
        self,
        name: str,
        memory_manager: Any,
        performance_monitor: Any,
        dispatcher: Any,
    ):
        self.name = name
        self.memory_manager = memory_manager
        self.performance_monitor = performance_monitor
        self.dispatcher = dispatcher

    @abstractmethod
    async def solve_task(self, task: str, **kwargs) -> Any:
        """
        Solves the given task.

        Args:
            task (str): The task description.
            **kwargs: Additional arguments.

        Returns:
            Any: Result of the task.
        """
        pass

    def describe_capabilities(self) -> str:
        """
        Describes the capabilities of the agent.

        Returns:
            str: Description of capabilities.
        """
        return "No description available."
