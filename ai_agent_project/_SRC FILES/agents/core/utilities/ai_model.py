# Path: ai_agent_project/src/agents/core/utilities/ai_model.py

from abc import ABC, abstractmethod
from typing import Dict

class AIModel(ABC):
    """
    Abstract base class for AI models.
    """

    @abstractmethod
    async def generate_fix(self, error_type: str, error_message: str) -> str:
        """
        Generate a fix suggestion based on the error type and message.
        
        Args:
            error_type (str): The type of error detected.
            error_message (str): The error message.
        
        Returns:
            str: The suggested fix.
        """
        pass
