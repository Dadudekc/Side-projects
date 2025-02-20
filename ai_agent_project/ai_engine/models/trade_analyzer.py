import numpy as np
import pandas as pd
import logging
from scipy.signal import argrelextrema

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TradeAnalyzer:
    """
    Analyzes market data and generates Tbow Tactic-based trade signals.
    
    Features:
    - Detects MACD curls (bullish/bearish crossovers).
    - Identifies support & resistance levels.
    - Recognizes trends for strategic entries & exits.
    """

    def __init__(self):
        self.window_size = 20  # Default window size for trend detection

    def calculate_macd(self, prices: pd.Series, short_window: int = 12, long_window: int = 26, signal_window: int = 9):
        """
        Calculates the MACD line, signal line, and histogram.

        Args:
            prices (pd.Series): Stock price data.
            short_window (int): Short EMA period (default: 12).
            long_window (int): Long EMA period (default: 26).
            signal_window (int): Signal EMA period (default: 9).

        Returns:
            pd.DataFrame: MACD, Signal line, and Histogram.
        """
        short_ema = prices.ewm(span=short_window, adjust=False).mean()
        long_ema = prices.ewm(span=long_window, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=signal_window, adjust=False).mean()
        histogram = macd - signal

        return pd.DataFrame({"MACD": macd, "Signal": signal, "Histogram": histogram})

    def detect_macd_curl(self, macd_data: pd.DataFrame):
        """
        Identifies bullish or bearish MACD curl patterns.

        Args:
            macd_data (pd.DataFrame): DataFrame with MACD and Signal line.

        Returns:
            str: "Bullish Curl" or "Bearish Curl" if detected, otherwise "No Curl".
        """
        if len(macd_data) < 2:
            return "No Curl"

        last_macd = macd_data["MACD"].iloc[-1]
        prev_macd = macd_data["MACD"].iloc[-2]
        last_signal = macd_data["Signal"].iloc[-1]
        prev_signal = macd_data["Signal"].iloc[-2]

        if prev_macd < prev_signal and last_macd > last_signal:
            return "Bullish Curl ✅ (MACD crossed above Signal)"
        elif prev_macd > prev_signal and last_macd < last_signal:
            return "Bearish Curl ❌ (MACD crossed below Signal)"
        
        return "No Curl"

    def identify_support_resistance(self, price_data: pd.Series):
        """
        Identifies key support and resistance levels using local minima/maxima.

        Args:
            price_data (pd.Series): Historical stock prices.

        Returns:
            dict: Support and resistance levels.
        """
        minima = price_data.iloc[argrelextrema(price_data.values, np.less_equal, order=self.window_size)[0]]
        maxima = price_data.iloc[argrelextrema(price_data.values, np.greater_equal, order=self.window_size)[0]]

        return {
            "Support Levels": minima.values.tolist(),
            "Resistance Levels": maxima.values.tolist()
        }

    def detect_trend(self, price_data: pd.Series):
        """
        Determines the trend direction based on moving averages.

        Args:
            price_data (pd.Series): Stock price data.

        Returns:
            str: "Uptrend", "Downtrend", or "Sideways".
        """
        short_ma = price_data.rolling(window=10).mean()
        long_ma = price_data.rolling(window=50).mean()

        if short_ma.iloc[-1] > long_ma.iloc[-1]:
            return "Uptrend 📈"
        elif short_ma.iloc[-1] < long_ma.iloc[-1]:
            return "Downtrend 📉"
      
