from ai_engine.models.memory.context_manager import ContextManager
from agents.core.AgentBase import AgentBase
import logging

class CustomAgent(AgentBase):
    """
    A customizable AI agent that learns from interactions, retrieves relevant memory,
    and adapts responses dynamically based on user inputs.

    This agent handles user interactions by checking its memory context for stored responses.
    If no prior response exists, it generates a fallback reply and stores the interaction for
    future reference. Additional methods allow it to describe its capabilities, process tasks,
    and perform a clean shutdown.
    """

    def __init__(self, name: str = "CustomAgent"):
        """
        Initializes the CustomAgent with a unique name.

        Args:
            name (str): The name of the agent (default: "CustomAgent").
        """
        super().__init__(name=name)
        self.name = name

    def describe_capabilities(self) -> str:
        """
        Returns a description of the agent's capabilities.

        Returns:
            str: A brief description of what the agent can do.
        """
        return "CustomAgent: Handles interactive queries with memory-based responses."

    def interact(self, user_input: str) -> str:
        """
        Processes user input by checking memory for a stored response or generating a new one.

        Args:
            user_input (str): The user's message.

        Returns:
            str: A response based on previous interactions or a new fallback message.
        """
        response = ContextManager.global_context.retrieve_memory(user_input)

        if response:
            return f"(Context-Aware) {response}"

        # Default fallback response for unknown queries
        response = "I'm still learning, but I will remember this for next time!"
        ContextManager.global_context.store_memory(user_input, response)

        return response

    def solve_task(self, task: str, **kwargs) -> dict:
        """
        Processes a task and returns a structured result.

        Args:
            task (str): The task to be performed.
            **kwargs: Additional parameters.

        Returns:
            dict: A dictionary with the result of the task.
        """
        if task == "interact":
            query = kwargs.get("query", "")
            return {"status": "success", "response": self.interact(query)}
        elif task == "describe":
            return {"status": "success", "description": self.describe_capabilities()}
        else:
            return {"status": "error", "message": f"Task '{task}' not recognized."}

    def shutdown(self) -> None:
        """
        Performs cleanup operations and logs a shutdown message.
        """
        logging.info(f"{self.name} is shutting down.")
