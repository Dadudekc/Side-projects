from agents.core.DebuggerAgent import DebuggerAgent

if __name__ == "__main__":
    debug_agent = DebuggerAgent()
    debug_agent.automate_debugging()  # 🚀 Fixes failing tests!
# scripts/run_debugger.py

from agents.core.DebuggerAgent import DebuggerAgent
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
