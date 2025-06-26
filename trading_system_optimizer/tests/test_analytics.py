from trading_system_optimizer.journal.trade_entry import TradeEntry
from trading_system_optimizer.analytics import performance_analyzer


def test_win_rate():
    entries = [
        TradeEntry(ticker="A", entry=1, exit=2),
        TradeEntry(ticker="B", entry=1, exit=0.5),
        TradeEntry(ticker="C", entry=1, exit=1.5),
    ]
    assert performance_analyzer.win_rate(entries) == 2/3
