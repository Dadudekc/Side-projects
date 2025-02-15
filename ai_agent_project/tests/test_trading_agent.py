import unittest
from unittest.mock import MagicMock, patch

from agents.core.AgentBase import AgentBase
from agents.core.utilities.ai_model_manager import AIModelManager
from agents.core.utilities.ai_patch_utils import AIPatchUtils
from agents.core.utilities.CustomAgent import CustomAgent
from agents.core.trading_agent import TradingAgent


class TestTradingAgent(unittest.TestCase):
    """Unit tests for the TradingAgent class."""

    def setUp(self):
        """Set up a fresh instance of TradingAgent for each test."""
        self.agent = TradingAgent(test_mode=True)

    def test_initialization(self):
        """Test if the TradingAgent initializes correctly."""
        self.assertEqual(self.agent.name, "TradingAgent")
        self.assertTrue(self.agent.test_mode)  # Should be in test mode

    def test_describe_capabilities(self):
        """Test the describe_capabilities method."""
        self.assertEqual(
            self.agent.describe_capabilities(),
            "Executes MACD-RSI trading strategy and executes trades using Alpaca API.",
        )

    def test_execute_trade_test_mode(self):
        """Test execute_trade in test mode."""
        result = self.agent.execute_trade("AAPL", "buy", 10)
        self.assertEqual(result["status"], "simulated execution")

    @patch("agents.TradingAgent.tradeapi.REST")
    def test_execute_trade_live_mode(self, mock_tradeapi):
        """Test execute_trade in live mode with mock Alpaca API."""
        mock_api_instance = MagicMock()
        mock_tradeapi.return_value = mock_api_instance

        self.agent.test_mode = False
        self.agent.alpaca = mock_api_instance

        result = self.agent.execute_trade("AAPL", "buy", 10)
        self.assertEqual(result["status"], "executed")
        mock_api_instance.submit_order.assert_called_once()

    @patch("agents.TradingAgent.tradeapi.REST")
    def test_execute_trade_failure(self, mock_tradeapi):
        """Test handling of trade execution failure."""
        mock_api_instance = MagicMock()
        mock_api_instance.submit_order.side_effect = Exception("API Error")
        mock_tradeapi.return_value = mock_api_instance

        self.agent.test_mode = False
        self.agent.alpaca = mock_api_instance

        result = self.agent.execute_trade("AAPL", "buy", 10)
        self.assertIn("error", result)

    def test_solve_task_fetch_market_data(self):
        """Test solve_task with market data retrieval."""
        result = self.agent.solve_task("fetch_market_data", symbol="AAPL")
        self.assertIn("error", result)  # Mock not implemented for fetch_market_data

    def test_solve_task_execute_trade(self):
        """Test solve_task with execute_trade task."""
        result = self.agent.solve_task(
            "execute_trade", symbol="AAPL", action="buy", quantity=5
        )
        self.assertEqual(result["status"], "simulated execution")

    def test_solve_task_unknown(self):
        """Test solve_task with an unknown task."""
        result = self.agent.solve_task("unknown_task")
        self.assertIn("error", result)

    def test_shutdown(self):
        """Test that shutdown logs properly."""
        with self.assertLogs(level="INFO") as log:
            self.agent.shutdown()
        self.assertTrue(
            any("TradingAgent is shutting down" in msg for msg in log.output)
        )


if __name__ == "__main__":
    unittest.main()
