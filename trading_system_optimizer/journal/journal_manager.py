"""Manage trade entries in the YAML journal file."""
from __future__ import annotations

from pathlib import Path
from typing import List
import yaml

from .trade_entry import TradeEntry
from ..config import TRADE_LOG_PATH


def load_entries(path: Path = TRADE_LOG_PATH) -> List[TradeEntry]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or []
    return [TradeEntry.from_dict(item) for item in raw]


def save_entries(entries: List[TradeEntry], path: Path = TRADE_LOG_PATH) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump([e.to_dict() for e in entries], f, sort_keys=False)


def append_entry(entry: TradeEntry, path: Path = TRADE_LOG_PATH) -> None:
    entries = load_entries(path)
    entries.append(entry)
    save_entries(entries, path)
