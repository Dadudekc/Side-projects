import os
import sys
import logging
import pytest
import tempfile
from unittest.mock import patch, mock_open
from agents.core.logger import logger, get_logs, LOG_LEVEL, console_handler, file_handler
import time


@pytest.fixture(scope="function", autouse=True)
def reset_logger():
    """Resets the logger between tests to ensure handlers are not duplicated."""
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def test_console_logging(capsys):
    """Test if logs are correctly output to the console."""
    logger.handlers.clear()  # Remove all handlers
    console_handler.stream = sys.stdout  # Ensure it's writing to stdout
    logger.addHandler(console_handler)  # Re-attach console handler

    logger.info("Test info message")

    # **NEW FIX: Add slight delay to ensure pytest captures stdout**
    time.sleep(0.1)

    # **Ensure logs are flushed before capturing**
    for handler in logger.handlers:
        handler.flush()

    captured = capsys.readouterr()
    print(f"Captured output: {captured.out}")  # Debugging output

    assert "Test info message" in captured.out, "Console log message not found!"

@pytest.fixture(scope="function")
def temp_log_file():
    """Creates a temporary log file for testing file logging."""
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        log_path = temp_file.name
    yield log_path

    # Ensure file handler is closed before deleting
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.close()
    
    os.remove(log_path)

def test_log_level_env_variable():
    """Test that logger respects the LOG_LEVEL environment variable."""
    with patch.dict(os.environ, {"LOG_LEVEL": "ERROR"}):
        from importlib import reload
        import agents.core.logger  # Re-import the module
        reload(agents.core.logger)

        assert logging.getLevelName(agents.core.logger.logger.level) == "ERROR"

def test_file_logging(temp_log_file):
    """Test if logs are correctly written to the log file."""
    logger.handlers.clear()  # Remove all handlers

    # Create a new file handler for this test
    test_file_handler = logging.FileHandler(temp_log_file, mode="w", encoding="utf-8")
    test_file_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(test_file_handler)

    logger.error("File log test")
    test_file_handler.flush()  # Ensure log is written before reading

    with open(temp_log_file, "r", encoding="utf-8") as f:
        log_content = f.read()
        print(f"Log content: {log_content}")  # Debugging output
        assert "File log test" in log_content, "File log message not found!"

    # Close handler before fixture cleanup
    test_file_handler.close()
    logger.removeHandler(test_file_handler)


def test_get_logs(temp_log_file):
    """Test retrieval of logs from file."""
    with patch("builtins.open", mock_open(read_data="Retrieving logs test\n")):
        logs = get_logs()
        assert any("Retrieving logs test" in line for line in logs)


def test_get_logs_empty():
    """Test `get_logs()` when log file does not exist."""
    with patch("os.path.exists", return_value=False):
        assert get_logs() == []


def test_logger_has_correct_handlers():
    """Test that the logger has two handlers (console + file)."""
    print(f"Handlers: {logger.handlers}")  # Debugging output
    assert len(logger.handlers) >= 2  # At least two handlers should exist
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    assert any(isinstance(h, logging.handlers.RotatingFileHandler) for h in logger.handlers)


def test_colored_formatter():
    """Test that ColoredFormatter applies ANSI colors correctly."""
    from agents.core.logger import ColoredFormatter
    formatter = ColoredFormatter("%(levelname)s - %(message)s")

    record = logging.LogRecord(
        name="test", level=logging.WARNING, pathname="test", lineno=10, msg="Warning test", args=(), exc_info=None
    )

    formatted_message = formatter.format(record)
    assert "\033[93mWARNING\033[0m" in formatted_message  # Yellow color expected


if __name__ == "__main__":
    pytest.main()
