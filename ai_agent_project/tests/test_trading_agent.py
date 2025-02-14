import unittest
from agents.core.TradingAgent import TradingAgent

class TestTradingAgent(unittest.TestCase):
    """Unit tests for TradingAgent."""

    def setUp(self):
        """Set up a fresh instance of TradingAgent for each test."""
        self.agent = TradingAgent(test_mode=True)

    def test_evaluate_strategy_buy_signal(self):
        """Test evaluation function when a BUY signal is expected."""
        market_data = {"macd": 0.6, "rsi": 25, "symbol": "AAPL"}
        result = self.agent.evaluate_strategy("AAPL")
        self.assertIn("BUY recommendation", result)

    def test_evaluate_strategy_hold(self):
        """Test evaluation function when a HOLD signal is expected."""
        market_data = {"macd": 0.0, "rsi": 50, "symbol": "AAPL"}
        result = self.agent.evaluate_strategy("AAPL")
        self.assertIn("HOLD recommendation", result)

    def test_evaluate_strategy_sell_signal(self):
        """Test evaluation function when a SELL signal is expected."""
        market_data = {"macd": -0.6, "rsi": 75, "symbol": "AAPL"}
        result = self.agent.evaluate_strategy("AAPL")
        self.assertIn("SELL recommendation", result)

    def test_execute_trade_invalid_action(self):
        """Test executing a trade with an invalid action."""
        result = self.agent.execute_trade("AAPL", "invalid_action", 10)
        self.assertIn("error", result)

    def test_execute_trade_invalid_quantity(self):
        """Test executing a trade with an invalid quantity."""
        result = self.agent.execute_trade("AAPL", "buy", 0)
        self.assertIn("error", result)

    def test_execute_trade_valid(self):
        """Test executing a valid trade order."""
        result = self.agent.execute_trade("AAPL", "buy", 10)
        self.assertEqual(result["status"], "simulated execution")

    def test_fetch_market_data_invalid(self):
        """Test fetching market data for an invalid symbol."""
        result = self.agent.fetch_market_data("INVALID")
        self.assertIn("error", result)

    def test_initialization(self):
        """Test TradingAgent initialization."""
        self.assertEqual(self.agent.name, "TradingAgent")

    def test_shutdown(self):
        """Test TradingAgent shutdown function."""
        self.agent.shutdown()
        self.assertTrue(True)  # Just ensuring no exceptions

if __name__ == "__main__":
    unittest.main()
