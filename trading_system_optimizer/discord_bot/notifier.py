"""Send trade notifications to Discord."""
import requests
from ..config import DISCORD_WEBHOOK_URL
from ..journal.trade_entry import TradeEntry


def notify_trade(entry: TradeEntry) -> None:
    if not DISCORD_WEBHOOK_URL:
        return
    data = {
        "content": f"New trade: {entry.ticker} at {entry.entry}",
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data, timeout=5)
    except requests.RequestException:
        pass
