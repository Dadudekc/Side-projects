import logging
import logging.handlers
import os
import sys
from importlib import reload

# Define log level (can be set via an environment variable or hardcoded)
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# Create a custom logger instance
logger = logging.getLogger("advanced_logger")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
logger.propagate = False  # Prevent logs from propagating to the root logger

# Define a colored formatter for console output using ANSI escape codes.
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        level_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{level_color}{record.levelname}{self.RESET}"
        return super().format(record)

# Console handler with color support.
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
console_formatter = ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

# File handler with rotation (max 10 MB per file, up to 5 backups)
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.log")
file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))
file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

# Add handlers to the logger if not already added.
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

def get_logs() -> list:
    """
    Retrieves the current log file content as a list of log entries.
    This can be used, for example, in a UI to show stored logs.
    """
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            return f.readlines()
    return []
