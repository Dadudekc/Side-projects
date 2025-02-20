import os
import sys
import logging

# Ensure the root directory is added to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ProjectLauncher")

try:
    # Importing core components
    from agents.core.trading_agent import TradingAgent
    from agents.core.journal_agent import JournalAgent
    from agents.agent_dispatcher import AgentDispatcher
    from ui.FixForge import main as launch_fixforge
    from agents.core.utilities.debugging_orchestrator import DebuggingOrchestrator
except ImportError as e:
    logger.error(f"❌ Import Error: {e}")
    sys.exit(1)

def initialize_agents():
    """Initialize all key agents and register them in the dispatcher."""
    logger.info("🔄 Initializing core AI agents...")

    dispatcher = AgentDispatcher()

    # Initialize required agents
    trading_agent = TradingAgent()
    journal_agent = JournalAgent()

    # Register agents
    dispatcher.register_agent("trading", trading_agent)
    dispatcher.register_agent("journal", journal_agent)

    logger.info("✅ Agents initialized and registered.")
    return dispatcher

def start_debugging_orchestrator():
    """Start the debugging orchestrator."""
    logger.info("🚀 Starting Debugging Orchestrator...")
    orchestrator = DebuggingOrchestrator()

    # Example debugging session to verify functionality
    orchestrator.start_debugging_session(
        task_description="Test Debugging Session",
        error_log="Example error log for verification"
    )

def launch_ui():
    """Launch the FixForge UI."""
    logger.info("🖥️ Launching FixForge UI...")
    launch_fixforge()

if __name__ == "__main__":
    logger.info("🔧 Starting AI Debugging Project...")

    # Initialize agents
    dispatcher = initialize_agents()

    # Start debugging orchestrator in the background
    start_debugging_orchestrator()

    # Launch UI
    launch_ui()
