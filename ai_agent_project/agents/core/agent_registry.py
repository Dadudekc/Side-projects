"""
Manages the registration, retrieval, and lifecycle of AI agents dynamically.

The AgentRegistry class provides a centralized mechanism to:
- Register, unregister, and retrieve AI agents.
- Validate agents against the `AgentBase` structure.
- Dynamically expand the registry for future AI agents.

Methods:
    - `register_agent(name: str, agent_instance: AgentBase) -> bool`
    - `unregister_agent(name: str) -> bool`
    - `get_agent(name: str) -> AgentBase | None`
    - `agent_exists(name: str) -> bool`
    - `list_agents() -> list[str]`
"""

import logging
from typing import Dict
from agents.core.AgentBase import AgentBase
from agents.core.professor_synapse_agent import ProfessorSynapseAgent
from agents.core.journal_agent import JournalAgent
from agents.core.memory_engine import MemoryEngine
from agents.core.gpt_forecasting import GPTForecaster
from agents.core.graph_memory import GraphMemory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AgentRegistry:
    """
    📌 Manages the registration, retrieval, and lifecycle of AI agents dynamically.
    """

    def __init__(self):
        """Initializes and registers core agents."""
        self.agents: Dict[str, AgentBase] = {}
        self.load_core_agents()
        logger.info(f"✅ AgentRegistry initialized with agents: {self.list_agents()}")

    def load_core_agents(self):
        """Registers core AI agents on initialization."""
        core_agents = {
            "professor": ProfessorSynapseAgent(),
            "forecasting": GPTForecaster(),
            "memory": MemoryEngine(),
            "graph": GraphMemory(),
            "journal": JournalAgent(),  # Fixed casing issue: "JournalAgent" → "journal"
        }

        for name, agent in core_agents.items():
            self.register_agent(name, agent)

    def register_agent(self, name: str, agent_instance: AgentBase) -> bool:
        """
        Dynamically registers a new agent if it inherits from AgentBase.

        Args:
            name (str): The unique name of the agent.
            agent_instance (AgentBase): The agent instance.

        Returns:
            bool: True if registered successfully, False if agent already exists or invalid.
        """
        if not isinstance(agent_instance, AgentBase):
            logger.error(f"❌ Attempted to register invalid agent '{name}' (not an AgentBase subclass).")
            return False

        if name in self.agents:
            logger.warning(f"⚠️ Agent '{name}' is already registered.")
            return False

        self.agents[name] = agent_instance
        logger.info(f"✅ Agent '{name}' registered successfully.")
        return True

    def unregister_agent(self, name: str) -> bool:
        """
        Removes an agent from the registry.

        Args:
            name (str): The name of the agent to remove.

        Returns:
            bool: True if removed successfully, False if agent not found.
        """
        if name in self.agents:
            del self.agents[name]
            logger.info(f"🗑️ Agent '{name}' unregistered successfully.")
            return True

        logger.warning(f"⚠️ Attempted to remove non-existent agent '{name}'.")
        return False

    def get_agent(self, name: str) -> AgentBase | None:
        """
        Retrieves an agent by name.

        Args:
            name (str): The name of the agent.

        Returns:
            AgentBase | None: The agent instance or None if not found.
        """
        agent = self.agents.get(name)
        if agent:
            return agent

        logger.warning(f"❌ Agent '{name}' not found in registry.")
        return None

    def agent_exists(self, name: str) -> bool:
        """
        Checks if an agent exists in the registry.

        Args:
            name (str): The agent's name.

        Returns:
            bool: True if the agent exists, False otherwise.
        """
        return name in self.agents

    def list_agents(self) -> list[str]:
        """
        Lists all registered agent names.

        Returns:
            list[str]: A list of available agent names.
        """
        return list(self.agents.keys())
