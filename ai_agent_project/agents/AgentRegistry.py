import os
import logging
import importlib
from agents.core.utilities.AgentBase import AgentBase  # ✅ Use AgentBase instead of IAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AgentRegistry:
    """
    Manages the registration and retrieval of AI agents.
    """

    def __init__(self, agents_dir="agents.core"):
        """
        Initializes the agent registry and loads agents from the specified directory.
        """
        self.agents = {}
        self.agents_dir = agents_dir
        self.load_agents()

    def load_agents(self):
        """Dynamically loads agent modules."""
        try:
            base_module = self.agents_dir.replace("/", ".")
            agent_files = ["JournalAgent", "TradingAgent", "DebuggerAgent"]  # ✅ Add DebuggerAgent

            for agent_name in agent_files:
                try:
                    module_path = f"{base_module}.{agent_name}"
                    module = importlib.import_module(module_path)
                    agent_class = getattr(module, agent_name)
                    
                    # ✅ Ensure the loaded class is a valid subclass of AgentBase
                    if issubclass(agent_class, AgentBase) and agent_class is not AgentBase:
                        self.agents[agent_name] = agent_class()
                        logger.info(f"Loaded agent: {agent_name}")
                    else:
                        logger.warning(f"Skipping {agent_name}, as it is not a subclass of AgentBase.")

                except Exception as e:
                    logger.error(f"Failed to load agent module {module_path}: {e}")

        except Exception as e:
            logger.error(f"Error loading agents: {e}")

    def get_agent(self, name):
        """Retrieves an agent by name."""
        return self.agents.get(name)

    def list_agents(self):
        """Returns a list of registered agents."""
        return list(self.agents.keys())
