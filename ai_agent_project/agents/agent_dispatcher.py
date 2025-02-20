"""
A module to dispatch tasks to multiple specialized AI agents.
It auto-discovers agent subclasses (classes inheriting from AgentBase)
in the 'agents' package and supports manual registration of core agents.
It also supports external third-party models via adapters.
"""

import importlib
import json
import logging
import pkgutil
from typing import Any, Dict

from agents.core.AgentBase import AgentBase
from agents.core.agent_registry import AgentRegistry
from agents.core.professor_synapse_agent import ProfessorSynapseAgent
from agents.core.memory_engine import MemoryEngine
from agents.core.gpt_forecasting import GPTForecaster
from agents.core.graph_memory import GraphMemory

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
if not logger.handlers:
    logger.addHandler(handler)


class AgentDispatcher:
    """
    🚀 Dispatches tasks to specialized AI agents while managing and validating them dynamically.

    This implementation auto-discovers agent subclasses in the "agents" package and also registers
    a core set of agents manually via the AgentRegistry. External agents (via adapters) can be
    registered manually as well.
    """

    def __init__(self) -> None:
        # Instantiate AgentRegistry for manual registration.
        self.registry = AgentRegistry()
        # Initialize the agents dictionary.
        self.agents: Dict[str, Any] = {}
        # Auto-discover agent subclasses.
        try:
            self._discover_agents()
        except Exception as e:
            logger.error(f"Auto-discovery failed: {e}")
        # Manually register core agents.
        self.agents.update({
            "professor": ProfessorSynapseAgent(),
            "forecasting": GPTForecaster(),
            "memory": MemoryEngine(),
            "graph": GraphMemory(),
        })
        # Validate that all agents are proper.
        self._validate_agents()
        logger.info("✅ AgentDispatcher initialized.")
        logger.info(f"🛠 Available Agents: {list(self.agents.keys())}")
        if not self.agents:
            logger.warning("⚠️ No agents were loaded into the registry!")

    def _discover_agents(self) -> None:
        """
        Automatically discovers and registers all agent subclasses in the 'agents' package.
        This method iterates over modules in the package and attempts to instantiate any
        class that is a subclass of AgentBase (excluding AgentBase itself). Errors during
        instantiation are caught and logged.
        """
        package_name = "agents"
        try:
            package = importlib.import_module(package_name)
        except ModuleNotFoundError:
            logger.error(f"❌ Package '{package_name}' not found.")
            return

        for finder, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package_name + "."):
            try:
                module = importlib.import_module(module_name)
            except Exception as e:
                logger.error(f"❌ Failed to import module '{module_name}': {e}")
                continue
            for obj_name in dir(module):
                obj = getattr(module, obj_name)
                if (
                    isinstance(obj, type)
                    and issubclass(obj, AgentBase)
                    and obj is not AgentBase
                ):
                    try:
                        agent_instance = obj()  # Assumes a no-argument constructor.
                        self.register_agent(obj_name.lower(), agent_instance)
                        logger.info(f"✅ Registered agent: {obj_name.lower()}")
                    except Exception as e:
                        logger.error(f"❌ Failed to instantiate agent '{obj_name}': {e}")

    def register_agent(self, agent_name: str, agent_instance: Any) -> None:
        """
        Registers an agent instance with a specified name.
        """
        if not isinstance(agent_instance, AgentBase):
            logger.error(f"❌ Agent '{agent_name}' does not inherit from AgentBase.")
            return
        if agent_name not in self.agents:
            self.agents[agent_name] = agent_instance
        else:
            logger.warning(f"⚠️ Agent '{agent_name}' is already registered.")

    def _validate_agents(self) -> None:
        """
        Ensures all registered agents inherit from AgentBase.
        """
        for name, agent in list(self.agents.items()):
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
        # Use case-insensitive lookup.
        key = agent_name.lower()
        agent = self.agents.get(key)
        if not agent:
            logger.error(f"❌ Agent '{key}' not found.")
            return json.dumps({"error": f"Agent '{key}' not found."})
        if not isinstance(agent, AgentBase):
            logger.error(f"❌ Agent '{key}' does not inherit from AgentBase.")
            return json.dumps({"error": f"Agent '{key}' is invalid."})
        try:
            # Extract "action" from task_data and separate additional arguments.
            action_value = task_data.get("action")
            other_args = {k: v for k, v in task_data.items() if k != "action"}
            if hasattr(agent, "solve_task"):
                response = agent.solve_task(action_value, **other_args)
            elif hasattr(agent, "handle_task"):
                response = agent.handle_task(task_data)
            else:
                raise AttributeError("Agent does not implement a task handling method.")
            return json.dumps(response)
        except Exception as e:
            logger.exception(f"⚠️ Error executing task for '{key}': {e}")
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

    result = dispatcher.dispatch_task("professor", sample_task)
    print(result)
