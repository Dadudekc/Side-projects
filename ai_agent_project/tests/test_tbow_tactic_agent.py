import unittest
from unittest.mock import patch, MagicMock
from agents.core.tbow_tactic_agent import TbowTacticAgent
from agents.core.utilities.tbow_scanner import TbowScanner
from agents.core.utilities.tbow_trade_executor import TbowTradeExecutor

class TestTbowTacticAgent(unittest.TestCase):
    @patch.object(TbowScanner, 'detect_macd_curl', return_value=True)
    @patch.object(TbowTradeExecutor, 'place_order', return_value={"status": "filled"})
    def test_execute_trading_strategy(self, mock_trade_executor, mock_scanner):
        """Test the full agent execution pipeline."""
        agent = TbowTacticAgent("api_key", "api_secret", "https://paper-api.alpaca.markets")
        agent.execute_trading_strategy("AAPL", 10)

        mock_scanner.assert_called_once()
        mock_trade_executor.assert_called_once_with("AAPL", 10, side="buy")

    @patch.object(TbowTradeExecutor, 'get_position', return_value={"current_price": "120"})
    @patch.object(TbowTradeExecutor, 'close_position', return_value=True)
    def test_manage_risk(self, mock_close_position, mock_get_position):
        """Test risk management logic."""
        agent = TbowTacticAgent("api_key", "api_secret", "https://paper-api.alpaca.markets")
        agent.manage_risk("AAPL", 110, 130)

        mock_get_position.assert_called_once()
        mock_close_position.assert_not_called()  # Price is within normal range

    @patch.object(TbowTradeExecutor, 'get_position', return_value={"current_price": "100"})
    @patch.object(TbowTradeExecutor, 'close_position', return_value=True)
    def test_stop_loss_trigger(self, mock_close_position, mock_get_position):
        """Test if stop-loss triggers position closure."""
        agent = TbowTacticAgent("api_key", "api_secret", "https://paper-api.alpaca.markets")
        agent.manage_risk("AAPL", 105, 130)

        mock_get_position.assert_called_once()
        mock_close_position.assert_called_once()  # Stop-loss triggered

if __name__ == '__main__':
    unittest.main()
