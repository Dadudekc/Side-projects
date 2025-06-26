"""Configuration constants for trading system optimizer."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TRADE_LOG_PATH = BASE_DIR / "trade_log.yaml"
DISCORD_WEBHOOK_URL = ""  # Fill with your Discord webhook URL
