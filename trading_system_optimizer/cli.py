import argparse
import sys
from pathlib import Path

# Allow running as a script without installing the package
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from trading_system_optimizer.journal.trade_entry import TradeEntry
from trading_system_optimizer.journal import journal_manager


def main(argv=None):
    parser = argparse.ArgumentParser(description="Log a trade via CLI")
    parser.add_argument("ticker", help="Ticker symbol")
    parser.add_argument("entry", type=float, help="Entry price")
    parser.add_argument("--exit", type=float, help="Exit price", default=None)
    parser.add_argument("--notes", help="Trade notes", default="")
    parser.add_argument(
        "--log-path",
        type=str,
        default=str(journal_manager.TRADE_LOG_PATH),
        help="Path to YAML log file",
    )
    args = parser.parse_args(argv)

    entry = TradeEntry(ticker=args.ticker, entry=args.entry, exit=args.exit, notes=args.notes)
    journal_manager.append_entry(entry, Path(args.log_path))
    print("Trade logged:", entry.to_dict())


if __name__ == "__main__":
    main()
