from trading_system_optimizer.journal.trade_entry import TradeEntry
from trading_system_optimizer.journal import journal_manager


def test_append_and_load(tmp_path):
    path = tmp_path / "log.yaml"
    entry = TradeEntry(ticker="TEST", entry=1.0, exit=1.2)
    journal_manager.append_entry(entry, path)
    entries = journal_manager.load_entries(path)
    assert len(entries) == 1
    assert entries[0].ticker == "TEST"
    assert entries[0].exit == 1.2
