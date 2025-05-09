"""

This module provides ErrorParser class for parsing pytest output to extract test failure details.

The ErrorParser class uses a regex (regular expression) pattern to search through a pytest output 
string and find information about test failures.

The main methods include:
    - __init__: Initializes the ErrorParser object with a regex pattern for parsing pytest outputs.
    - parse_test_failures: This method accepts a string of pytest output, applies the regex
        pattern to find failing tests, and returns a list of
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ErrorParser:
    """
    Parses pytest output to extract test failure details.
    """

    def __init__(self):
        """
        Initializes the ErrorParser with a compiled regex pattern for efficiency.
        """
        self.failure_pattern = re.compile(
            r"FAILED\s*-?\s*([\w./]+)\s*(::|\s*:\s*)([\w\[\]<>]+)\s*[-:]\s*(.+)",
            re.MULTILINE
        )

    def parse_test_failures(self, test_output: str) -> List[Dict[str, str]]:
        """
        Parses pytest output and extracts structured failure details.

        Args:
            test_output (str): The raw pytest output.

        Returns:
            List[Dict[str, str]]: A list of failure details, each containing:
                - "file": Test file where the failure occurred.
                - "test": Name of the failing test function.
                - "error": The error message or reason for failure.
        """
        if not test_output or not isinstance(test_output, str):
            logger.warning("⚠️ Invalid or empty test output received for parsing.")
            return []

        logger.info("🔍 Parsing test failures from output...")
        failures = []

        for match in self.failure_pattern.finditer(test_output):
            file_name = match.group(1).strip()
            test_name = match.group(3).strip()
            error_msg = match.group(4).strip()

            failure = {"file": file_name, "test": test_name, "error": error_msg}
            logger.debug(f"✅ Detected failure: {failure}")

            failures.append(failure)

        total_failures = len(failures)
        if total_failures > 0:
            logger.info(f"📉 Found {total_failures} test failure(s).")
        else:
            logger.info("✅ No test failures detected.")

        return failures
