from typing import Dict, Any, List
from typing import Dict, List
import os
import logging
import alpaca_trade_api as tradeapi
from agents.core.core import AgentBase


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TradingAgent(AgentBase):
    """
    TradingAgent Class

    Executes trades based on MACD & RSI strategy using Alpaca’s API.
    """

    def __init__(self, name: str = "TradingAgent", project_name: str = "AI_Trading_System", test_mode: bool = None):
        """Initializes the TradingAgent with Alpaca API credentials."""
        super().__init__(name=name, project_name=project_name)

        # Force test mode in testing environments
        if test_mode is None:
            test_mode = os.getenv("TEST_MODE") == "1"

        self.test_mode = test_mode

        self.alpaca_api_key = os.getenv("ALPACA_API_KEY", "demo")
        self.alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY", "demo")
        self.alpaca_base_url = "https://paper-api.alpaca.markets"  # Use paper trading

        if not self.test_mode and (self.alpaca_api_key == "demo" or self.alpaca_secret_key == "demo"):
            logger.error("Missing Alpaca API credentials! Running in test mode.")
            self.test_mode = True

        if not self.test_mode:
            self.alpaca = tradeapi.REST(
                self.alpaca_api_key, self.alpaca_secret_key, self.alpaca_base_url, api_version="v2"
            )
            logger.info(f"{self.name} initialized with Alpaca Trading API.")

    def execute_trade(self, symbol: str, action: str, quantity: int):
        """Executes a trade order."""
        if self.test_mode:
            return {"symbol": symbol, "action": action, "quantity": quantity, "status": "simulated execution"}

        try:
            order = self.alpaca.submit_order(
                symbol=symbol,
                qty=quantity,
                side=action,
                type="market",
                time_in_force="gtc",
            )
            logger.info(f"Trade executed: {action} {quantity} shares of {symbol}")
            return {"symbol": symbol, "action": action, "quantity": quantity, "status": "executed"}
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return {"error": str(e)}

    def describe_capabilities(self):
        """Returns capabilities of TradingAgent."""
        return "Executes MACD-RSI trading strategy and executes trades using Alpaca API."

    def solve_task(self, task: str, **kwargs):
        """Handles tasks dynamically for trading-related operations."""
        if task == "fetch_market_data":
            return self.fetch_market_data(kwargs.get("symbol", "AAPL"))
        elif task == "execute_trade":
            return self.execute_trade(kwargs.get("symbol", "AAPL"), kwargs.get("action", "buy"), kwargs.get("quantity", 1))
        elif task == "evaluate_strategy":
            return self.evaluate_strategy(kwargs.get("symbol", "AAPL"))
        else:
            return {"error": "Unknown task"}

    def shutdown(self):
        """Gracefully shuts down the trading agent."""
        logger.info(f"{self.name} is shutting down.")
