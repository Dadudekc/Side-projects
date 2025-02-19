import logging
import alpaca_trade_api as tradeapi
from typing import Dict, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TbowTradeExecutor:
    """
    Handles trade execution for Tbow Tactic AI using the Alpaca API.
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str):
        """
        Initializes the Alpaca API client.

        Args:
            api_key (str): Alpaca API key.
            api_secret (str): Alpaca API secret.
            base_url (str): Alpaca API base URL.
        """
        self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    def place_order(self, symbol: str, qty: int, side: str, order_type: str = "market", time_in_force: str = "gtc") -> Optional[Dict]:
        """
        Places an order using Alpaca API.

        Args:
            symbol (str): The stock symbol to trade.
            qty (int): Quantity of shares/contracts.
            side (str): "buy" or "sell".
            order_type (str, optional): Type of order (default is "market").
            time_in_force (str, optional): Time in force (default is "gtc").

        Returns:
            Optional[Dict]: Order confirmation details, or None if order fails.
        """
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force
            )
            logger.info(f"Order placed: {order}")
            return order._raw
        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            return None

    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Retrieves current position for a given stock.

        Args:
            symbol (str): The stock symbol.

        Returns:
            Optional[Dict]: Position details, or None if no position exists.
        """
        try:
            position = self.api.get_position(symbol)
            return position._raw
        except Exception as e:
            logger.warning(f"No position found for {symbol}: {e}")
            return None

    def close_position(self, symbol: str) -> bool:
        """
        Closes an open position.

        Args:
            symbol (str): The stock symbol to close.

        Returns:
            bool: True if the position was closed successfully, False otherwise.
        """
        try:
            self.api.close_position(symbol)
            logger.info(f"Position closed for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to close position for {symbol}: {e}")
            return False
