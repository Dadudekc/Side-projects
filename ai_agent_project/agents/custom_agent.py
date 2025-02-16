from ai_engine.models.memory.context_manager import ContextManager

class CustomAgent:
    """
    A customizable AI agent that learns from interactions, retrieves relevant memory,
    and adapts responses dynamically based on user inputs.
    """

    def __init__(self, name: str = "CustomAgent"):
        """
        Initializes the CustomAgent with a unique name.
        
        Args:
            name (str): The name of the agent (default: "CustomAgent").
        """
        self.name = name

    def interact(self, user_input: str) -> str:
        """
        Handles interaction by retrieving memory-based responses or storing new inputs.

        Args:
            user_input (str): The user's message.

        Returns:
            str: The agent's response based on memory or a fallback message.
        """
        response = ContextManager.global_context.retrieve_memory(user_input)
        
        if response:
            return f"(Context-Aware) {response}"
        
        # Default fallback response for unknown queries
        response = "I'm still learning, but I will remember this for next time!"
        ContextManager.global_context.store_memory(user_input, response)
        
        return response
