"""

This Python module contains the TradingAgent class that utilizes Alpaca API to execute trades. The TradingAgent is derived from the AgentBase class.

Module level imports:
os: Provides a portable way of using operating system dependent functionality.
logging: Provides a flexible framework for emitting log messages from Python programs.
alpaca_trade_api: API that enables interactions with Alpaca's trading platform. (optional)
        
AgentBase class is imported as base class for the TradingAgent.

Attributes:
ALP
"""

import os
import logging
from typing import Dict, Any
from agents.core.AgentBase import AgentBase

try:
    import alpaca_trade_api as tradeapi
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logging.warning("Alpaca Trade API not installed. Live trading disabled.")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TradingAgent(AgentBase):
    """
    A Trading Agent that executes trades using the Alpaca API or simulates trades in test mode.
    Executes trades based on MACD & RSI strategy.
    """

    def __init__(self, name: str = "TradingAgent", project_name: str = "FreeRideInvestor", test_mode: bool = None):
        """Initializes the TradingAgent with Alpaca API credentials."""
        super().__init__(name=name, project_name=project_name)

        # Determine test mode (environment variable or parameter)
        if test_mode is None:
            test_mode = os.getenv("TEST_MODE") == "1"

        self.test_mode = test_mode
        self.alpaca = None

        # Load API credentials
        self.alpaca_api_key = os.getenv("ALPACA_API_KEY", "demo")
        self.alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY", "demo")
        self.alpaca_base_url = "https://paper-api.alpaca.markets"  # Use paper trading

        # Validate credentials
        if not self.test_mode and (self.alpaca_api_key == "demo" or self.alpaca_secret_key == "demo"):
            logger.error("Missing Alpaca API credentials! Running in test mode.")
            self.test_mode = True

        # Initialize Alpaca API if live trading is enabled
        if not self.test_mode and ALPACA_AVAILABLE:
            self.alpaca = tradeapi.REST(
                self.alpaca_api_key, self.alpaca_secret_key, self.alpaca_base_url, api_version="v2"
            )
            logger.info(f"{self.name} initialized with Alpaca Trading API.")

    def describe_capabilities(self) -> str:
        """
        Returns the capabilities of the TradingAgent.

        Returns:
            str: A description of the agent's capabilities.
        """
        return "Executes MACD-RSI trading strategy and executes trades using Alpaca API."

    def execute_trade(self, symbol: str, action: str, quantity: int) -> Dict[str, Any]:
        """
        Executes a trade (real or simulated).

        Args:
            symbol (str): The stock symbol to trade.
            action (str): "buy" or "sell".
            quantity (int): Number of shares.

        Returns:
            Dict[str, Any]: Trade execution details.
        """
        if self.test_mode:
            logger.info(f"[SIMULATED] {action.upper()} {quantity} shares of {symbol}")
            return {"status": "simulated execution", "symbol": symbol, "action": action, "quantity": quantity}

        if not ALPACA_AVAILABLE or self.alpaca is None:
            logger.error("Alpaca API is not available.")
            return {"error": "Alpaca API not available"}

        try:
            order = self.alpaca.submit_order(
                symbol=symbol,
                qty=quantity,
                side=action,
                type="market",
                time_in_force="gtc"
            )
            logger.info(f"Trade executed: {action.upper()} {quantity} shares of {symbol}")
            return {"status": "executed", "order_id": order.id, "symbol": symbol, "action": action, "quantity": quantity}

        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return {"error": f"Trade execution failed: {str(e)}"}

    def solve_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
        """
        Handles different trading tasks.

        Args:
            task_type (str): The type of task.
            **kwargs: Additional parameters.

        Returns:
            Dict[str, Any]: Task execution details or error message.
        """
        if task_type == "fetch_market_data":
            return {"error": "Market data retrieval not implemented"}

        if task_type == "execute_trade":
            return self.execute_trade(kwargs.get("symbol"), kwargs.get("action"), kwargs.get("quantity"))

        if task_type == "evaluate_strategy":
            return {"error": "Strategy evaluation not implemented"}

        return {"error": f"Unsupported task type '{task_type}'"}

    def shutdown(self):
        """Gracefully shuts down the TradingAgent."""
        logger.info(f"{self.name} is shutting down.")
