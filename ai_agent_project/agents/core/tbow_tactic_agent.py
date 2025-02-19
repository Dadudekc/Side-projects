import logging
from agents.core.utilities.tbow_scanner import TbowScanner
from agents.core.utilities.tbow_trade_executor import TbowTradeExecutor

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TbowTacticAgent:
    """
    The main trading agent that combines market scanning and trade execution.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str):
        """
        Initializes the Tbow Tactic Agent.

        Args:
            api_key (str): Alpaca API key.
            api_secret (str): Alpaca API secret.
            base_url (str): Alpaca API base URL.
        """
        self.scanner = TbowScanner()
        self.executor = TbowTradeExecutor(api_key, api_secret, base_url)

    def execute_trading_strategy(self, symbol: str, qty: int):
        """
        Runs the trading strategy by scanning for a MACD curl and placing trades.

        Args:
            symbol (str): The stock symbol to trade.
            qty (int): Number of shares/contracts to trade.
        """
        logger.info(f"Scanning market for {symbol}...")
        if self.scanner.detect_macd_curl():
            logger.info(f"MACD curl detected for {symbol}. Placing buy order...")
            order = self.executor.place_order(symbol, qty, side="buy")
            if order:
                logger.info(f"Trade executed: {order}")
            else:
                logger.error("Trade execution failed.")
        else:
            logger.info(f"No MACD curl detected for {symbol}. No trade executed.")

    def manage_risk(self, symbol: str, stop_loss: float, take_profit: float):
        """
        Manages risk by setting stop-loss and take-profit levels.

        Args:
            symbol (str): The stock symbol being traded.
            stop_loss (float): Price at which to trigger a stop-loss.
            take_profit (float): Price at which to trigger take-profit.
        """
        position = self.executor.get_position(symbol)
        if position:
            current_price = float(position["current_price"])
            if current_price <= stop_loss:
                logger.info(f"Stop-loss triggered for {symbol}. Closing position...")
                self.executor.close_position(symbol)
            elif current_price >= take_profit:
                logger.info(f"Take-profit triggered for {symbol}. Closing position...")
                self.executor.close_position(symbol)
        else:
            logger.info(f"No open position found for {symbol}.")
