import logging
from agents.AgentRegistry import AgentRegistry
from agents.core.AgentDispatcher import AgentDispatcher

def main():
    """
    Main entry point to showcase the AI agent project.
    Demonstrates initialization of multiple agents, and
    how to dispatch tasks to them.
    """

    # 1. Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # 2. Initialize Agent Registry
    registry = AgentRegistry()
    registry.load_agents()  # Load all agents from the 'agents/' folder
    logger.info("Agent Registry initialized and agents loaded.")

    # 3. Create an Agent Dispatcher
    dispatcher = AgentDispatcher()
    logger.info("Agent Dispatcher created.")

    # 4. Example usage: Dispatch tasks to TradingAgent
    # (If your TradingAgent relies on environment variables for Alpaca, ensure they are set or test_mode=True.)
    task_data_fetch = {
        "action": "fetch_market_data",
        "symbol": "AAPL"
    }
    fetch_result = dispatcher.dispatch_task("TradingAgent", task_data_fetch)
    logger.info(f"Fetch market data result: {fetch_result}")

    task_data_evaluate = {
        "action": "evaluate_strategy",
        "symbol": "AAPL"
    }
    eval_result = dispatcher.dispatch_task("TradingAgent", task_data_evaluate)
    logger.info(f"Evaluate strategy result: {eval_result}")

    task_data_trade = {
        "action": "execute_trade",
        "symbol": "AAPL",
        "quantity": 1,
        "side": "buy"
    }
    trade_result = dispatcher.dispatch_task("TradingAgent", task_data_trade)
    logger.info(f"Execute trade result: {trade_result}")

    # 5. Example usage: Use AgentActor to run shell/python tasks (if available)
    # This is optional and depends on how your AgentActor is integrated in your environment
    # For demonstration, only logs a placeholder if not set up
    try:
        shell_task = "echo Hello from AgentActor"
        shell_result = dispatcher.dispatch_task("AgentActor", {"task": shell_task})
        logger.info(f"Shell task result: {shell_result}")

        python_task = "python: print('AgentActor running Python code!')"
        python_result = dispatcher.dispatch_task("AgentActor", {"task": python_task})
        logger.info(f"Python task result: {python_result}")

    except Exception as e:
        logger.warning(f"AgentActor tasks not set up or missing. Error: {e}")

    # 6. Show usage of JournalAgent or DebuggerAgent (if you have them loaded)
    # The exact usage depends on how your tasks are structured.
    # Example:
    try:
        journal_result = dispatcher.dispatch_task("JournalAgent", {"action": "create", "title": "Demo Entry", "content": "Testing JournalAgent."})
        logger.info(f"Journal Agent result: {journal_result}")
    except Exception as e:
        logger.warning(f"JournalAgent usage not set up. Error: {e}")

    logger.info("Done showcasing the AI agent system.")

if __name__ == "__main__":
    main()
