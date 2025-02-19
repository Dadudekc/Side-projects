"""
A module to dispatch tasks to multiple specialized AI agents. It provides a way to manage and validate dynamic task assignment among various agent subclasses. These tasks are dispatched to the requested agent and ensure structured task execution.
In case of any exception, it is also handled and the appropriate response is sent.
Using this module, Agents can be effectively managed and utilized. The module also provides easy logging of various activities during the execution of tasks assigned to various agents.
"""

import logging
import json
from typing import Dict, Any

from agents.core.agent_registry import AgentRegistry
from agents.core.AgentBase import AgentBase
from agents.core.professor_synapse_agent import ProfessorSynapseAgent
from agents.core.gpt_forecasting import GPTForecaster
from agents.core.graph_memory import GraphMemory
from agents.core.memory_engine import MemoryEngine
from agents.core.journal_agent import JournalAgent

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
if not logger.handlers:  # Only add handler if none exist.
    logger.addHandler(handler)

class AgentDispatcher:
    """
    🚀 Dispatches tasks to specialized AI agents while managing and validating them dynamically.
    """
    def __init__(self) -> None:
        """
        Initializes the AgentDispatcher, loads registered agents, and ensures validation.
        """
        self.registry = AgentRegistry()
        # Normalize keys to lower-case for consistency.
        self.agents: Dict[str, AgentBase] = {
            "professor": ProfessorSynapseAgent(),
            "forecasting": GPTForecaster(),
            "memory": MemoryEngine(),
            "graph": GraphMemory(),
            "journal": JournalAgent(),
        }
        self._validate_agents()
        logger.info("✅ AgentDispatcher initialized.")
        available_agents = list(self.agents.keys())
        logger.info(f"🛠 Available Agents: {available_agents}")
        if not available_agents:
            logger.warning("⚠️ No agents were loaded into the registry!")

    def _validate_agents(self) -> None:
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
        key = agent_name.lower()
        agent = self.agents.get(key) or self.registry.get_agent(key)
        if not agent:
            logger.error(f"❌ Agent '{key}' not found.")
            return json.dumps({"error": f"Agent '{key}' not found."})
        if not isinstance(agent, AgentBase):
            logger.error(f"❌ Agent '{key}' does not inherit from AgentBase.")
            return json.dumps({"error": f"Agent '{key}' is invalid."})
        try:
            response = agent.solve_task(task_data.get("action"), **task_data)
            return json.dumps(response)
        except Exception as e:
            logger.exception(f"⚠️ Error executing task for '{key}': {e}")
            return json.dumps({"error": f"Task execution failed: {str(e)}"})

# Example usage (when run as a script)
if __name__ == "__main__":
    dispatcher = AgentDispatcher()
    sample_task = {
        "action": "create",
        "title": "Agent Registry Test",
        "content": "Testing integration with the dispatcher.",
        "tags": ["test", "registry"],
    }
    result = dispatcher.dispatch_task("journal", sample_task)
    print(result)
