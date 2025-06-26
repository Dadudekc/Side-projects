from trading_system_optimizer.journal.trade_entry import TradeEntry
from trading_system_optimizer.discord_bot import notifier


def test_notify_trade(monkeypatch):
    called = {}

    def fake_post(url, json, timeout):
        called['url'] = url
        called['json'] = json
        called['timeout'] = timeout

    monkeypatch.setattr('requests.post', fake_post)
    monkeypatch.setattr(notifier, 'DISCORD_WEBHOOK_URL', 'http://example.com')
    entry = TradeEntry(ticker='A', entry=1.0)
    notifier.notify_trade(entry)
    assert called['json']['content'].startswith('New trade')
