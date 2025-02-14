# Path: ai_agent_project/src/agents/plugins/example_plugin.py

from plugin_interface import AgentPlugin
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

def run_task(data):
    """
    Example plugin task function.
    
    Args:
        data (dict): Data passed to the plugin.
    
    Returns:
        str: Result of the plugin task.
    """
    input_data = data.get("input", "No input provided.")
    return f"Plugin executed with input: {input_data}"