import logging
import json
from agents.AgentRegistry import AgentRegistry
from agents.core.utilities.AgentBase import AgentBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AgentDispatcher:
    """
    Manages and executes tasks for registered AI agents.
    Ensures each agent implements AgentBase before dispatching tasks to it.
    """

    def __init__(self):
        """
        Initializes the AgentDispatcher and loads available agents.
        """
        self.registry = AgentRegistry()  
        self.agents = self.registry.list_agents()

        if not self.agents:
            logger.warning("No agents were loaded into the registry!")

        logger.info("AgentDispatcher initialized.")
        logger.info(f"Available Agents: {self.agents}")  # ✅ Log available agents correctly

    def dispatch_task(self, agent_name: str, task_data: dict) -> str:
        """
        Dispatches a task to the requested agent.

        Args:
            agent_name (str): The name of the agent to handle the task.
            task_data (dict): The task data including the action and other parameters.

        Returns:
            str: A JSON-encoded response from the agent.
        """
        agent = self.registry.get_agent(agent_name)
        if not agent:
            logger.error(f"Agent '{agent_name}' not found in registry.")
            return json.dumps({"error": f"Agent '{agent_name}' not found."})

        if not isinstance(agent, AgentBase):
            logger.error(f"Agent '{agent_name}' does not inherit from AgentBase.")
            return json.dumps({"error": f"Agent '{agent_name}' is invalid."})

        try:
            response = agent.solve_task(task_data.get("action"), **task_data)
            return json.dumps(response)  # ✅ Ensure response is always JSON
        except Exception as e:
            logger.error(f"Error executing task for '{agent_name}': {e}")
            return json.dumps({"error": f"Task execution failed: {str(e)}"})

# Example Usage
if __name__ == "__main__":
    dispatcher = AgentDispatcher()

    sample_task = {
        "action": "create",
        "title": "Agent Registry Test",
        "content": "Testing integration with the dispatcher.",
        "tags": ["test", "registry"]
    }

    result = dispatcher.dispatch_task("JournalAgent", sample_task)
    print(result)
