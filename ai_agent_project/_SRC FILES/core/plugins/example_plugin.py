# Path: ai_agent_project/src/agents/plugins/example_plugin.py

from ai_agent_project.src.agents.plugins.plugin_interface import AgentPlugin
import logging

logger = logging.getLogger(__name__)

class ExampleAgent(AgentPlugin):
    """
    Example agent plugin implementing the AgentPlugin interface.
    """

    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        logger.info(f"ExampleAgent '{self.name}' initialized with parameters: {kwargs}")

    async def solve_task(self, task: str, **kwargs) -> str:
        logger.info(f"ExampleAgent '{self.name}' solving task: {task}")
        # Implement task solving logic here
        result = f"ExampleAgent '{self.name}' executed task: {task}"
        logger.debug(f"ExampleAgent '{self.name}' result: {result}")
        return result

    def describe_capabilities(self) -> str:
        return "ExampleAgent can execute basic tasks and provide example responses."

def run_task(task_data: dict) -> str:
    """
    Example plugin task that processes input data and returns a result.
    
    Args:
        task_data (dict): Data required for the task.
        
    Returns:
        str: Result of the task.
    """
    input_data = task_data.get("input", "")
    # Perform some processing (e.g., reversing the input string)
    processed_data = input_data[::-1]
    return f"Processed data: {processed_data}"
