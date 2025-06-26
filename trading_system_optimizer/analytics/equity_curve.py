"""Generate equity curve plots."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable
import matplotlib.pyplot as plt

from ..journal.trade_entry import TradeEntry


def plot_equity_curve(entries: Iterable[TradeEntry], path: Path) -> None:
    values = []
    equity = 1.0
    for e in entries:
        if e.exit is not None:
            equity *= (1 + (e.exit - e.entry) / e.entry)
        values.append(equity)
    plt.figure()
    plt.plot(values)
    plt.title("Equity Curve")
    plt.xlabel("Trades")
    plt.ylabel("Equity")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
