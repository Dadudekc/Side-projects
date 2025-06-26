"""Post end of day summary to Discord."""
import requests
from ..config import DISCORD_WEBHOOK_URL
from ..journal import journal_manager
from .formatter import format_summary


def post_summary() -> None:
    if not DISCORD_WEBHOOK_URL:
        return
    entries = journal_manager.load_entries()
    summary = format_summary(entries)
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": summary}, timeout=5)
    except requests.RequestException:
        pass
