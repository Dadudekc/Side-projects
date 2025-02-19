"""
debugger_runner.py

A Python module that integrates testing and debugging using pytest, ErrorParser, and AutoFixer.

Key Features:
- Runs automated tests using pytest.
- Parses test failures with ErrorParser.
- Applies automated fixes using AutoFixer.
- Retries test runs up to a configurable limit.
- Uses structured logging to track debugging progress.

Classes:
    DebuggerRunner: Manages test execution, failure analysis, fix application, and retry attempts.

DebuggerRunner Methods:
    - __init__: Initializes ErrorParser and AutoFixer.
    - run_tests: Runs all tests using pytest and returns the output.
    - retry_tests: Retries failed tests with automated fixes up to a max retry count.
"""

import logging
import subprocess
from ai_engine.models.debugger.error_parser import ErrorParser
from ai_engine.models.debugger.auto_fixer import AutoFixer

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DebuggerRunner:
    """
    Coordinates the testing and debugging process by:
      - Running tests via pytest.
      - Analyzing failures using ErrorParser.
      - Attempting automated fixes with AutoFixer.
      - Retrying tests until they pass or max retries are reached.
    """
    def __init__(self):
        """
        Initializes the DebuggerRunner by setting up:
          - ErrorParser for identifying failed tests and their causes.
          - AutoFixer for applying automated code patches.
        """
        self.parser = ErrorParser()
        self.fixer = AutoFixer()

    def run_tests(self) -> str:
        """
        Runs all tests using pytest and returns the combined output (stdout + stderr).

        Returns:
            str: The output of the pytest execution.
        """
        logger.info("🚀 Running tests with pytest...")
        try:
            result = subprocess.run(
                ["pytest", "tests", "--maxfail=5", "--tb=short", "-q"],
                capture_output=True, text=True
            )
            return result.stdout + result.stderr
        except Exception as e:
            logger.error(f"❌ Failed to execute tests: {e}")
            return f"Error: {e}"

    def retry_tests(self, max_retries: int = 3) -> bool:
        """
        Runs tests and retries failed ones up to a maximum number of attempts,
        applying automated fixes as necessary.

        Args:
            max_retries (int): The maximum number of retry attempts.

        Returns:
            bool: True if all tests pass after retries, False otherwise.
        """
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Test run attempt {attempt} of {max_retries}")
            output = self.run_tests()
            failures = self.parser.parse_test_failures(output)

            if not failures:
                logger.info("✅ All tests passed!")
                return True  # Exit early if no failures

            logger.info(f"📉 {len(failures)} test(s) failed. Attempting to apply fixes...")

            fixes_applied = 0
            for failure in failures:
                if self.fixer.apply_fix(failure):
                    fixes_applied += 1
                    logger.info(f"✅ Fix applied for {failure.get('file', 'unknown file')}")
                else:
                    logger.warning(f"⚠️ No fix available for {failure.get('file', 'unknown file')}")

            if fixes_applied == 0:
                logger.error("❌ No fixes were applied in this attempt. Aborting retry process.")
                return False

        logger.error("❌ Max retries reached. Some tests are still failing.")
        return False

if __name__ == "__main__":
    runner = DebuggerRunner()
    success = runner.retry_tests()

    if success:
        logger.info("🎉 All tests passed after automated debugging!")
    else:
        logger.error("❌ Automated debugging could not resolve all test failures.")
