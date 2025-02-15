import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ErrorParser:
    """
    Parses pytest output to extract structured test failure details.
    """

    def __init__(self):
        """
        Initializes the ErrorParser with a precompiled regex pattern for efficiency.
        """
        self.failure_pattern = re.compile(
            r"FAILED\s+([^\s:]+)::([^\s]+)\s*-\s*(.+)", re.MULTILINE
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
        if not isinstance(test_output, str) or not test_output.strip():
            logger.warning("⚠️ Invalid or empty test output received for parsing.")
            return []

        logger.info("🔍 Parsing test failures from output...")

        failures = [
            {"file": match.group(1).strip(), "test": match.group(2).strip(), "error": match.group(3).strip()}
            for match in self.failure_pattern.finditer(test_output)
        ]

        total_failures = len(failures)
        if total_failures:
            logger.info(f"📉 Found {total_failures} test failure(s).")
        else:
            logger.info("✅ No test failures detected.")

        return failures
