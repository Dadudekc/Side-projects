"""

This module consists of a DebuggerLogger class which is designed to log debugging attempts including patch attempts, failures and successes.
The logs are stored in memory as well as appended to a log file. 

The DebuggerLogger has the following methods:
- log_attempt: This method logs a single debugging attempt by accepting failure details, a patch description, and a success indicator. The log is then added to the in-memory logs and written to the log file.
- _write_log: This is a private method
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("DebuggerLogger")
logger.setLevel(logging.DEBUG)

LOG_FILE = "debugger_attempts.log"

class DebuggerLogger:
    """
    Logs debugging attempts including patch attempts, failures, and successes.

    Logs are stored in-memory and appended to a log file.
    """

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log_attempt(self, failure: Dict[str, str], patch_description: str, success: bool):
        """
        Logs a debugging attempt.

        Args:
            failure (Dict[str, str]): Dictionary containing details about the failure.
                Expected keys: "file", "error".
            patch_description (str): A description of the patch attempted.
            success (bool): True if the patch was successfully applied; otherwise False.
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": failure.get("file", "Unknown"),
            "error": failure.get("error", "No error message provided"),
            "patch": patch_description,
            "success": success
        }
        self.logs.append(log_entry)
        self._write_log(log_entry)
        logger.info(f"Logged debugging attempt: {log_entry}")

    def _write_log(self, log_entry: Dict[str, Any]):
        """
        Appends a single log entry to the log file.
        """
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write log entry: {e}")

    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Returns the list of logged debugging attempts.
        """
        return self.logs

    def clear_logs(self):
        """
        Clears the in-memory logs and deletes the log file if it exists.
        """
        self.logs = []
        if os.path.exists(LOG_FILE):
            try:
                os.remove(LOG_FILE)
                logger.info("Cleared log file.")
            except Exception as e:
                logger.error(f"Failed to clear log file: {e}")
