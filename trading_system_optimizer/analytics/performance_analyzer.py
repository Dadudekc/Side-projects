"""Basic performance analytics functions."""
from __future__ import annotations

from statistics import mean
from typing import Iterable

from ..journal.trade_entry import TradeEntry


def win_rate(entries: Iterable[TradeEntry]) -> float:
    wins = [e for e in entries if e.exit and e.exit > e.entry]
    total = len([e for e in entries if e.exit is not None])
    return len(wins) / total if total else 0.0


def average_gain(entries: Iterable[TradeEntry]) -> float:
    gains = [((e.exit - e.entry) / e.entry) for e in entries if e.exit]
    return mean(gains) if gains else 0.0
