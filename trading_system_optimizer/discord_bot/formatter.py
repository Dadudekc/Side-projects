"""Format Discord messages."""
from typing import Iterable
from ..journal.trade_entry import TradeEntry


def format_summary(entries: Iterable[TradeEntry]) -> str:
    lines = [f"{e.ticker}: {e.entry} -> {e.exit}" for e in entries if e.exit]
    return "\n".join(lines) if lines else "No trades recorded."
