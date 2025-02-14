# Example Plugin: ai_agent_project/src/agents/tasks/debugger_agent.py

from plugins.plugin_interface import AgentPlugin
import logging

logger = logging.getLogger(__name__)

class DebuggerAgent(AgentPlugin):
    def __init__(self, name: str, memory_manager, performance_monitor, dispatcher):
        super().__init__(name, memory_manager, performance_monitor, dispatcher)
        logger.info(f"{self.name} initialized.")

    async def solve_task(self, task: str, **kwargs) -> str:
        logger.info(f"{self.name} solving task: {task}")
        # Implement task solving logic here
        return f"Task '{task}' solved by {self.name}."

    def describe_capabilities(self) -> str:
        return "Debugs code by detecting and fixing errors."
