"""
A module to dispatch tasks to multiple specialized AI agents.
It auto-discovers agents (classes inheriting from AgentBase) and supports
external third-party models via adapters.
"""

import logging
import json
import importlib
import pkgutil
from typing import Dict, Any

from agents.core.AgentBase import AgentBase

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
if not logger.handlers:
    logger.addHandler(handler)

class AgentDispatcher:
    """
    Dispatches tasks to specialized AI agents by auto-discovering agent classes.
    
    External agents (via adapters) can be registered manually.
    """

    def __init__(self) -> None:
        self.agents: Dict[str, Any] = {}  # Accept any type; we validate later.
        self._discover_agents()
        self._validate_agents()
        logger.info("✅ AgentDispatcher initialized.")
        logger.info(f"🛠 Available Agents: {list(self.agents.keys())}")
        if not self.agents:
            logger.warning("⚠️ No agents were loaded into the registry!")

    def _discover_agents(self) -> None:
        """
        Automatically discovers and registers all agent subclasses in the 'agents' package.
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
                        agent_instance = obj()  # Assumes a no-arg constructor.
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
        Validates that all registered agents inherit from AgentBase.
        If an invalid agent is found, it is removed from the registry.
        """
        for name, agent in list(self.agents.items()):
            if not isinstance(agent, AgentBase):
                logger.error(f"❌ Agent '{name}' does not inherit from AgentBase.")
                del self.agents[name]

    def dispatch_task(self, agent_name: str, task_data: Dict[str, Any]) -> str:
        """
        Dispatches a task to the requested agent.

        Args:
            agent_name (str): Name of the agent (case-insensitive).
            task_data (dict): Task parameters.

        Returns:
            str: A JSON-encoded response from the agent.
        """
        key = agent_name.lower()
        agent = self.agents.get(key)
        if not agent:
            logger.error(f"❌ Agent '{key}' not found.")
            return json.dumps({"error": f"Agent '{key}' not found."})
        if not isinstance(agent, AgentBase):
            logger.error(f"❌ Agent '{key}' does not inherit from AgentBase.")
            return json.dumps({"error": f"Agent '{key}' is invalid."})
        try:
            # Extract the action value and remove it from task_data to avoid duplication.
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
