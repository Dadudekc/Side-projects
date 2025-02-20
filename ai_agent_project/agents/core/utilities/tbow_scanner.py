import logging
from typing import Dict, List

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TbowScanner:
    """
    A scanner that detects MACD curl setups for trading strategies and provides
    additional analytical metrics.
    """

    def __init__(self) -> None:
        pass

    def fetch_market_data(self) -> Dict[str, List]:
        """
        Mock method for fetching market data.
        Actual implementation will use API calls.

        Returns:
            Dict[str, List]: A dictionary containing timestamps, MACD, and signal line values.
        """
        return {
            'timestamp': [],
            'macd': [],
            'signal': []
        }

    def detect_macd_curl(self) -> bool:
        """
        Detects a MACD curl event where the MACD crosses above the signal line.
        It verifies that there is at least one prior data point where MACD was below the signal,
        and that the latest data point shows MACD above the signal.

        Returns:
            bool: True if a valid MACD curl is detected, False otherwise.
        """
        market_data = self.fetch_market_data()
        macd: List[float] = market_data.get('macd', [])
        signal: List[float] = market_data.get('signal', [])

        # Check that MACD and signal data are non-empty and of equal length.
        if len(macd) < 2 or len(signal) < 2:
            logger.debug("Not enough data points for MACD crossover detection.")
            return False

        if len(macd) != len(signal):
            logger.error("Mismatched data lengths: MACD and signal lists must be the same length.")
            return False

        # Check if any previous data point had MACD below the signal.
        was_below = any(macd[i] < signal[i] for i in range(len(macd) - 1))
        # Check if the latest data point shows MACD above the signal.
        crosses_above = macd[-1] > signal[-1]

        valid_crossover = was_below and crosses_above

        logger.debug(
            f"MACD (last 3): {macd[-3:] if len(macd) >= 3 else macd}, "
            f"Signal (last 3): {signal[-3:] if len(signal) >= 3 else signal} | "
            f"Was Below: {was_below}, Crossed Above: {crosses_above}, "
            f"Detected: {valid_crossover}"
        )

        return valid_crossover

    def calculate_macd_slope(self) -> List[float]:
        """
        Calculates the slope (difference) between consecutive MACD values.

        Returns:
            List[float]: A list containing the slope values between consecutive MACD points.
        """
        market_data = self.fetch_market_data()
        macd: List[float] = market_data.get('macd', [])
        slopes = []
        if len(macd) < 2:
            logger.debug("Not enough data points to calculate MACD slopes.")
            return slopes

        for i in range(1, len(macd)):
            slope = macd[i] - macd[i - 1]
            slopes.append(slope)
        logger.debug(f"Calculated MACD slopes: {slopes}")
        return slopes

    def analyze_curl_strength(self) -> float:
        """
        Analyzes the strength of the detected MACD curl.
        If a valid curl is detected, returns the difference between MACD and signal at the latest data point.
        Otherwise, returns 0.0.

        Returns:
            float: The strength of the MACD curl.
        """
        if not self.detect_macd_curl():
            logger.debug("No valid MACD curl detected; curl strength is 0.0.")
            return 0.0

        market_data = self.fetch_market_data()
        macd: List[float] = market_data.get('macd', [])
        signal: List[float] = market_data.get('signal', [])

        curl_strength = macd[-1] - signal[-1]
        logger.debug(f"Detected MACD curl strength: {curl_strength}")
        return curl_strength
