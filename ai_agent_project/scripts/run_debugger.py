"""

This script allows you to run an AI-Powered Self-Healing Debugging System. The script imports the necessary tools from the core, logger and config utils and initializes the DebuggerAgent. The Agent is then run and begins fixing failing tests.

The script also sets up a logger for managing log messages and a configuration object for setting up configurable settings or options. 

Each of the aforementioned processes are consolidated within a main function, which is readily executed when the script is run.

"""

from agents.core.core import DebuggerAgent

if __name__ == "__main__":
    debug_agent = DebuggerAgent()
    debug_agent.automate_debugging()  # 🚀 Fixes failing tests!
# scripts/run_debugger.py

from agents.core.core import DebuggerAgent
from utils.logger import setup_logger
from utils.config import load_config

def main():
    # Initialize logging and configuration
    logger = setup_logger()
    config = load_config()

    logger.info("Starting AI-Powered Self-Healing Debugging System...")

    # Initialize the main debugging agent with configuration and logger
    debugger = DebuggerAgent(config=config, logger=logger)

    # Run the automated debugging loop
    debugger.run()

if __name__ == "__main__":
    main()
