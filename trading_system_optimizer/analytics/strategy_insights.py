"""Placeholder for strategy insights analysis."""

from typing import Iterable

from ..journal.trade_entry import TradeEntry


def unique_tickers(entries: Iterable[TradeEntry]) -> set[str]:
    return {e.ticker for e in entries}
