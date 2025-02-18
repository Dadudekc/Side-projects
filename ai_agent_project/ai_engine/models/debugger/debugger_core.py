import logging
import subprocess
from typing import List, Dict, Optional

# Import core debugging components
from ai_engine.models.debugger.test_runner import TestRunner
from ai_engine.models.debugger.error_parser import ErrorParser
from ai_engine.models.debugger.auto_fix_manager import AutoFixManager
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager
from ai_engine.models.debugger.rollback_manager import RollbackManager
from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy
from ai_engine.models.debugger.learning_db import LearningDB
from ai_engine.models.debugger.report_manager import ReportManager
from ai_engine.models.debugger.debug_agent_auto_fixer import DebugAgentAutoFixer
from ai_engine.models.debugger.debugger_logger import DebuggerLogger
from ai_engine.models.debugger.debugger_reporter import DebuggerReporter
from ai_engine.models.debugger.project_context_analyzer import ProjectContextAnalyzer

logger = logging.getLogger("DebugAgent")
logger.setLevel(logging.DEBUG)


class DebugAgent:
    """
    🚀 AI-powered debugging agent that automates test failure analysis, applies fixes, and validates corrections.
    """

    MAX_ATTEMPTS = 3

    def __init__(self, enable_ai_fixes: bool = True):
        """Initialize DebugAgent with key debugging components."""
        self.enable_ai_fixes = enable_ai_fixes
        self.test_runner = TestRunner()
        self.error_parser = ErrorParser()
        self.auto_fixer = AutoFixManager()
        self.patch_tracker = PatchTrackingManager()
        self.rollback_manager = RollbackManager()
        self.debugging_strategy = DebuggingStrategy()
        self.learning_db = LearningDB()
        self.report_manager = ReportManager()
        self.pre_debug_fixer = DebugAgentAutoFixer()
        self.logger = DebuggerLogger()
        self.reporter = DebuggerReporter()
        self.context_analyzer = ProjectContextAnalyzer()

    def run_debug_cycle(self, max_retries: int = MAX_ATTEMPTS) -> Dict[str, str]:
        """
        Runs a full debugging cycle:
        1️⃣ Executes tests.
        2️⃣ Analyzes failures.
        3️⃣ Applies AI-driven or learned fixes.
        4️⃣ Validates fixes by re-running tests.
        5️⃣ Logs and reports results.
        """
        logger.info("🚀 Starting AI DebugAgent session...")
        self.pre_debug_fixer.auto_fix_before_debugging()

        # Step 1: Run Tests
        test_output = self.test_runner.run_tests_simple()
        failures = self.error_parser.parse_test_failures(test_output)

        if not failures:
            logger.info("✅ All tests passed! No debugging needed.")
            return {"status": "success", "message": "All tests passed!"}

        logger.warning(f"⚠️ {len(failures)} test failures detected. Attempting fixes...")

        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Debugging attempt {attempt}/{max_retries}...")

            fixes_applied = False
            for failure in failures:
                fixes_applied |= self._attempt_fix(failure)

            if fixes_applied:
                test_output = self.test_runner.run_tests_simple()
                failures = self.error_parser.parse_test_failures(test_output)

                if not failures:
                    logger.info("✅ All fixes were successful!")
                    return {"status": "success", "message": "All tests fixed!"}

                logger.warning(f"📉 {len(failures)} tests still failing.")

        logger.error("❌ Max retries reached. Rolling back changes...")
        for failure in failures:
            self.rollback_manager.restore_backup(failure["file"])

        self.reporter.generate_report(failures)
        return {"status": "error", "message": "Some tests are still failing after fixes."}

    def _attempt_fix(self, failure: Dict[str, str]) -> bool:
        """
        Attempts to fix a failing test using AI or learned fixes.
        """
        error_sig = self.learning_db.get_signature(failure)
        patch = self.learning_db.get_known_fix(error_sig) or None

        if not patch and self.enable_ai_fixes:
            patch = self.auto_fixer.apply_fix(failure)

        if patch:
            success = self.patch_tracker.record_successful_patch(error_sig, patch)
            if success:
                logger.info(f"✅ Fix applied successfully to {failure['file']}")
                return True

            logger.warning(f"❌ Failed to apply fix for {failure['file']}. Rolling back changes.")
            self.rollback_manager.restore_backup(failure["file"])

        return False


if __name__ == "__main__":
    agent = DebugAgent(enable_ai_fixes=True)
    result = agent.run_debug_cycle()
    logger.info(f"🛠️ Debugging completed: {result}")
