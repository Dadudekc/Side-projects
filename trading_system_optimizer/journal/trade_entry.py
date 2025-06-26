"""Data model for a trade journal entry."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import yaml


@dataclass
class TradeEntry:
    ticker: str
    entry: float
    exit: Optional[float] = None
    notes: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticker": self.ticker,
            "entry": self.entry,
            "exit": self.exit,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeEntry":
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict(), sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "TradeEntry":
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
