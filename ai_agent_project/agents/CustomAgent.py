from context_manager import global_context

class CustomAgent:
    """
    A customizable AI agent that learns from interactions, retrieves relevant memory, and adapts responses.
    """

    def __init__(self, name: str = "CustomAgent"):
        self.name = name

    def interact(self, user_input: str) -> str:
        """
        Handles interaction by using shared context.

        Args:
            user_input (str): The user's message.

        Returns:
            str: The agent's response.
        """
        response = global_context.retrieve_memory(user_input)
        if response:
            return f"(Context-Aware) {response}"

        # Default fallback response
        response = "I'm still learning, but I will remember this for next time!"
        global_context.store_memory(user_input, response)
        return response