import logging
import math
import unittest
from unittest.mock import patch
from agents.core.utilities.tbow_scanner import TbowScanner

# Set up logging for debugging in tests
logger = logging.getLogger("TestTbowScanner")
logger.setLevel(logging.DEBUG)

class TestTbowScanner(unittest.TestCase):

    @patch.object(TbowScanner, 'fetch_market_data')
    def test_macd_curl_detection(self, mock_fetch):
        """Test that the MACD curl is correctly detected based on mock market data."""
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02', '10:03'],
            'macd': [-0.6, -0.4, -0.2, 0.1],  # MACD crosses above signal in final step
            'signal': [-0.5, -0.4, -0.3, -0.2]
        }
        scanner = TbowScanner()
        result = scanner.detect_macd_curl()

        logger.debug(f"MACD: {mock_fetch.return_value['macd']}")
        logger.debug(f"Signal: {mock_fetch.return_value['signal']}")
        logger.debug(f"Test MACD Curl Detection - Expected: True, Got: {result}")

        self.assertTrue(result, "MACD curl detection failed when it should have detected a crossover.")

    @patch.object(TbowScanner, 'fetch_market_data')
    def test_no_macd_curl(self, mock_fetch):
        """Test that no MACD curl is detected when MACD remains below signal."""
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02'],
            'macd': [-0.6, -0.5, -0.4],  # MACD does not cross above signal
            'signal': [-0.5, -0.4, -0.3]
        }
        scanner = TbowScanner()
        result = scanner.detect_macd_curl()

        logger.debug(f"MACD: {mock_fetch.return_value['macd']}")
        logger.debug(f"Signal: {mock_fetch.return_value['signal']}")
        logger.debug(f"Test No MACD Curl - Expected: False, Got: {result}")

        self.assertFalse(result, "MACD curl detected when it should not have been.")

    @patch.object(TbowScanner, 'fetch_market_data')
    def test_edge_case_macd_touching_signal(self, mock_fetch):
        """Test edge case where MACD touches the signal line but doesn't cross it."""
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02'],
            'macd': [-0.5, -0.4, -0.3],  # MACD nearly equals signal at the last point
            'signal': [-0.6, -0.5, -0.3]
        }
        scanner = TbowScanner()
        result = scanner.detect_macd_curl()

        logger.debug(f"MACD: {mock_fetch.return_value['macd']}")
        logger.debug(f"Signal: {mock_fetch.return_value['signal']}")
        logger.debug(f"Test Edge Case (Touching) - Expected: False, Got: {result}")

        self.assertFalse(result, "MACD curl detected when it only touched the signal line but did not cross.")

    @patch.object(TbowScanner, 'fetch_market_data')
    def test_mismatched_data_lengths(self, mock_fetch):
        """Test that detection fails if MACD and signal lists have mismatched lengths."""
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01'],
            'macd': [-0.6, -0.4],
            'signal': [-0.5]  # Mismatched length
        }
        scanner = TbowScanner()
        result = scanner.detect_macd_curl()

        logger.debug(f"MACD: {mock_fetch.return_value['macd']}")
        logger.debug(f"Signal: {mock_fetch.return_value['signal']}")
        logger.debug(f"Test Mismatched Lengths - Expected: False, Got: {result}")

        self.assertFalse(result, "MACD curl detected with mismatched data lengths.")

    @patch.object(TbowScanner, 'fetch_market_data')
    def test_calculate_macd_slope(self, mock_fetch):
        """Test that the MACD slope is correctly calculated."""
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02', '10:03'],
            'macd': [0.1, 0.2, 0.15, 0.3],
            'signal': [0.0, 0.1, 0.1, 0.2]
        }
        scanner = TbowScanner()
        slopes = scanner.calculate_macd_slope()

        expected_slopes = [0.1, -0.05, 0.15]
        logger.debug(f"Calculated slopes: {slopes} | Expected slopes: {expected_slopes}")
        # Compare each element within a small tolerance to handle floating point imprecision.
        for calculated, expected in zip(slopes, expected_slopes):
            self.assertTrue(math.isclose(calculated, expected, rel_tol=1e-9),
                            f"Expected {expected}, got {calculated}")

    @patch.object(TbowScanner, 'fetch_market_data')
    def test_analyze_curl_strength(self, mock_fetch):
        """
        Test that analyze_curl_strength returns the correct value when a valid MACD curl is present,
        and returns 0.0 when there is no valid curl.
        """
        # Test valid curl case
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02', '10:03'],
            'macd': [-0.6, -0.4, -0.2, 0.1],
            'signal': [-0.5, -0.4, -0.3, -0.2]
        }
        scanner = TbowScanner()
        strength = scanner.analyze_curl_strength()
        expected_strength = 0.1 - (-0.2)  # Latest diff between MACD and signal
        logger.debug(f"Detected curl strength: {strength} | Expected: {expected_strength}")
        self.assertAlmostEqual(strength, expected_strength, msg="Curl strength not calculated correctly.")

        # Test no curl case
        mock_fetch.return_value = {
            'timestamp': ['10:00', '10:01', '10:02'],
            'macd': [-0.6, -0.5, -0.4],
            'signal': [-0.5, -0.4, -0.3]
        }
        strength = scanner.analyze_curl_strength()
        logger.debug(f"No curl detected, curl strength: {strength} | Expected: 0.0")
        self.assertEqual(strength, 0.0, "Curl strength should be 0.0 when no valid curl is detected.")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTbowScanner)
    runner = unittest.TextTestRunner()
    runner.run(suite)
