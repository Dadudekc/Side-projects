# Path: ai_agent_project/src/core/run_dispatcher.py

import asyncio
import sys
import os

# Add the project root directory to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agent_dispatcher import AgentDispatcher

async def main():
    agents_dir = "ai_agent_project/src/agents/tasks"  # Update path as needed
    dispatcher = AgentDispatcher(agents_directory=agents_dir)
    await dispatcher.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Dispatcher stopped by user.")
