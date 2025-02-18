import logging
import json
from typing import Dict, Any

from agents.core.agent_registry import AgentRegistry
from agents.core.AgentBase import AgentBase
from agents.core.professor_synapse_agent import ProfessorSynapseAgent
from agents.core.memory_engine import MemoryEngine
from agents.core.gpt_forecasting import GPTForecaster
from agents.core.graph_memory import GraphMemory
from agents.core.journal_agent import JournalAgent  # ✅ Ensuring JournalAgent is available

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AgentDispatcher:
    """
    🚀 Dispatches tasks to specialized AI agents while managing and validating them dynamically.
    """

    def __init__(self):
        """
        Initializes the AgentDispatcher, loads registered agents, and ensures validation.
        """
        self.registry = AgentRegistry()
        self.agents = {
            "professor": ProfessorSynapseAgent(),
            "forecasting": GPTForecaster(),
            "memory": MemoryEngine(),
            "graph": GraphMemory(),
            "JournalAgent": JournalAgent(),  # ✅ Registered JournalAgent
        }

        self._validate_agents()
        logger.info("✅ AgentDispatcher initialized.")
        logger.info(f"🛠 Available Agents: {list(self.agents.keys())}")

    def _validate_agents(self):
        """
        Ensures all registered agents inherit from AgentBase.
        """
        for name, agent in self.agents.items():
            if not isinstance(agent, AgentBase):
                logger.error(f"❌ Agent '{name}' does not inherit from AgentBase.")
                raise TypeError(f"Agent '{name}' is invalid.")

    def dispatch_task(self, agent_name: str, task_data: Dict[str, Any]) -> str:
        """
        📡 Dispatches a task to the requested agent and ensures structured task execution.

        Args:
            agent_name (str): The name of the agent to handle the task.
            task_data (dict): The task data including the action and other parameters.

        Returns:
            str: A JSON-encoded response from the agent.
        """
        agent = self.agents.get(agent_name)
        if not agent:
            logger.error(f"❌ Agent '{agent_name}' not found.")
            return json.dumps({"error": f"Agent '{agent_name}' not found."})

        try:
            response = agent.solve_task(task_data.get("action"), **task_data)
            return json.dumps(response)  # ✅ Ensures response is always JSON
        except Exception as e:
            logger.error(f"⚠️ Error executing task for '{agent_name}': {e}")
            return json.dumps({"error": f"Task execution failed: {str(e)}"})


# Example Usage
if __name__ == "__main__":
    dispatcher = AgentDispatcher()

    sample_task = {
        "action": "create",
        "title": "Agent Registry Test",
        "content": "Testing integration with the dispatcher.",
        "tags": ["test", "registry"],
    }

    result = dispatcher.dispatch_task("JournalAgent", sample_task)
    print(result)
