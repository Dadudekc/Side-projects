import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve API keys securely from environment
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# Ensure API keys are available
if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    raise ValueError("❌ Missing Alpaca API credentials! Set ALPACA_API_KEY and ALPACA_SECRET_KEY in your .env file.")

# Configure logging
logger = logging.getLogger(__name__)

class MarketData:
    """
    Fetches real-time market data for stock analysis.
    """

    def __init__(self):
        self.api_key = ALPACA_API_KEY
        self.secret_key = ALPACA_SECRET_KEY
        self.base_url = "https://data.alpaca.markets/v2"

    def get_stock_data(self, symbol: str) -> dict:
        """
        Fetches real-time stock data for a given symbol.

        Args:
            symbol (str): The stock ticker symbol.

        Returns:
            dict: Stock price and volume data.
        """
        try:
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key
            }
            response = requests.get(f"{self.base_url}/stocks/{symbol}/quotes", headers=headers)
            response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses
            data = response.json()

            if "quotes" in data and data["quotes"]:
                return data["quotes"][0]  # Return latest quote
            else:
                logger.warning(f"Stock data not found for {symbol}")
                return {"error": "Stock data not found"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return {"error": "Failed to fetch stock data"}

    def get_price(self, symbol: str) -> float:
        """
        Fetches the latest stock price for the given symbol.

        Args:
            symbol (str): The stock ticker symbol.

        Returns:
            float: The latest stock price.
        """
        stock_data = self.get_stock_data(symbol)
        if "askprice" in stock_data:  # Alpaca provides "askprice" in real-time data
            return float(stock_data["askprice"])
        else:
            logger.warning(f"Price data unavailable for {symbol}")
            return 0.0  # Return a default value if data is unavailable
