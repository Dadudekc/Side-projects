import unittest
from unittest.mock import patch
import logging
from agents.core.utilities.tbow_scanner import TbowScanner

# Set up logging for debugging
logger = logging.getLogger("TestTbowScanner")
logger.setLevel(logging.DEBUG)

class TestTbowScanner(unittest.TestCase):

    @patch('agents.core.utilities.tbow_scanner.TbowScanner.fetch_market_data')
    def test_macd_curl_detection(self, mock_fetch):
        """Test that the MACD curl is correctly detected based on mock market data."""
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02'],
            'macd': [-0.6, -0.3, 0.1],  # Clear MACD crossover above signal
            'signal': [-0.5, -0.4, -0.2]  # Signal remains below MACD
        }
        scanner = TbowScanner()
        result = scanner.detect_macd_curl()

        # Debug logging
        logger.debug(f"MACD Values: {mock_fetch.return_value['macd']}")
        logger.debug(f"Signal Values: {mock_fetch.return_value['signal']}")
        logger.debug(f"Test MACD Curl Detection - Expected: True, Got: {result}")

        self.assertTrue(result)

    @patch('agents.core.utilities.tbow_scanner.TbowScanner.fetch_market_data')
    def test_no_macd_curl(self, mock_fetch):
        """Test that no signal is generated when MACD does not curl above signal."""
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02'],
            'macd': [-0.6, -0.5, -0.4],  # No crossover, MACD stays below signal
            'signal': [-0.5, -0.4, -0.3]  # Signal line is above MACD
        }
        scanner = TbowScanner()
        result = scanner.detect_macd_curl()

        # Debug logging
        logger.debug(f"MACD Values: {mock_fetch.return_value['macd']}")
        logger.debug(f"Signal Values: {mock_fetch.return_value['signal']}")
        logger.debug(f"Test No MACD Curl - Expected: False, Got: {result}")

        self.assertFalse(result)

    @patch('agents.core.utilities.tbow_scanner.TbowScanner.fetch_market_data')
    def test_edge_case_macd_touching_signal(self, mock_fetch):
        """Test edge case where MACD touches the signal line but doesn't cross it."""
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02'],
            'macd': [-0.5, -0.4, -0.3],  # MACD and signal are nearly equal
            'signal': [-0.6, -0.5, -0.3]  # No clear crossover
        }
        scanner = TbowScanner()
        result = scanner.detect_macd_curl()

        # Debug logging
        logger.debug(f"MACD Values: {mock_fetch.return_value['macd']}")
        logger.debug(f"Signal Values: {mock_fetch.return_value['signal']}")
        logger.debug(f"Test Edge Case (MACD touching signal) - Expected: False, Got: {result}")

        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
