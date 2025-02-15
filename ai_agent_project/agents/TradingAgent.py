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


class TradingAgent(AgentBase):
    


    """
    A Trading Agent that executes trades using the Alpaca API or simulates trades in test mode.
    """

    def __init__(self, test_mode=False):
        """
        Initialize the TradingAgent.

        Args:
            test_mode (bool): If True, trades are simulated instead of executed live.
        """
        super().__init__("TradingAgent", project_name="FreeRideInvestor")  # ✅ Added project_name
        self.test_mode = test_mode
        self.alpaca = None

        if not test_mode and ALPACA_AVAILABLE:
            self.alpaca = tradeapi.REST()  # Requires API keys in environment variables

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

        return {"error": f"Unsupported task type '{task_type}'"}

    def shutdown(self):
        """
        Shuts down the TradingAgent.
        """
        logger.info("TradingAgent is shutting down.")
