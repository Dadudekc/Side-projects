import unittest
from unittest.mock import patch, MagicMock
from agents.core.utilities.tbow_trade_executor import TbowTradeExecutor

class TestTbowTradeExecutor(unittest.TestCase):
    
    @patch('alpaca_trade_api.REST')
    def test_place_order(self, mock_alpaca):
        """Test order placement logic with mocked Alpaca API."""
        mock_api = mock_alpaca.return_value
        mock_order = MagicMock()
        mock_order._raw = {"id": "12345", "status": "filled"}
        mock_api.submit_order.return_value = mock_order

        executor = TbowTradeExecutor("api_key", "api_secret", "base_url")
        result = executor.place_order("AAPL", 10, "buy")

        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "filled")

    @patch('alpaca_trade_api.REST')
    def test_get_position(self, mock_alpaca):
        """Test retrieving position data."""
        mock_api = mock_alpaca.return_value
        mock_position = MagicMock()
        mock_position._raw = {"symbol": "AAPL", "qty": "10"}
        mock_api.get_position.return_value = mock_position

        executor = TbowTradeExecutor("api_key", "api_secret", "base_url")
        result = executor.get_position("AAPL")

        self.assertIsNotNone(result)
        self.assertEqual(result["symbol"], "AAPL")

    @patch('alpaca_trade_api.REST')
    def test_close_position(self, mock_alpaca):
        """Test closing a position."""
        mock_api = mock_alpaca.return_value
        mock_api.close_position.return_value = True

        executor = TbowTradeExecutor("api_key", "api_secret", "base_url")
        result = executor.close_position("AAPL")

        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
