import subprocess
from pathlib import Path


def test_cli_logs_trade(tmp_path):
    log_file = tmp_path / "log.yaml"
    cli_script = Path(__file__).resolve().parent.parent / "cli.py"
    subprocess.check_call([
        "python",
        str(cli_script),
        "AAPL",
        "100",
        "--exit",
        "110",
        "--notes",
        "test",
        "--log-path",
        str(log_file),
    ])
    assert log_file.exists()
    data = log_file.read_text()
    assert "AAPL" in data
