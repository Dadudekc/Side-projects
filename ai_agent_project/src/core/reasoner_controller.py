from ai_agent_project.src.agents.core.utilities.ChainOfThoughtReasoner import ChainOfThoughtReasoner
from AgentDispatcher import AgentDispatcher

class ReasonerController:
    """
    Controller for managing interaction between the GUI and ChainOfThoughtReasoner.
    """

    def __init__(self):
        # Initialize the dispatcher and reasoner
        self.agent_dispatcher = AgentDispatcher()
        self.reasoner = ChainOfThoughtReasoner(self.agent_dispatcher)

    def handle_task(self, task: str) -> str:
        """
        Processes a task using the ChainOfThoughtReasoner and returns the result.
        
        Args:
            task (str): The task input by the user.

        Returns:
            str: The result of the reasoning process.
        """
        agent_name = "DebuggingAgent"  # Example agent name
        result = self.reasoner.solve_task_with_reasoning(task, agent_name)
        return result
