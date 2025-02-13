# Path: ai_agent_project/src/core/run_dispatcher.py

import asyncio
from AgentDispatcher import AgentDispatcher
from utilities.memory_manager import MemoryManager
from utilities.ai_agent_utils import PerformanceMonitor

if __name__ == "__main__":
    # Initialize managers
    memory_manager = MemoryManager()
    performance_monitor = PerformanceMonitor()

    # Initialize dispatcher with the path to agent plugins
    dispatcher = AgentDispatcher(
        agents_directory="plugins",
        model_name="mistral-model",
        ollama_url="http://localhost:11434",
        max_retries=3,
    )

    # Optionally, add specific agents if not loaded via plugins
    # from agents.AIAgentWithMemory import AIAgentWithMemory
    # ai_agent = AIAgentWithMemory(
    #     name="aiagentwithmemory",
    #     project_name="AI_Debugger_Assistant",
    #     memory_manager=memory_manager,
    #     performance_monitor=performance_monitor,
    #     dispatcher=dispatcher
    # )
    # dispatcher.add_agent(ai_agent)

    # Run the dispatcher
    asyncio.run(dispatcher.run())
