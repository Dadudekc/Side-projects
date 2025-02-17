import logging
from typing import Optional, List, Dict, Any
from ai_engine.models.debugger.test_runner import TestRunner
from ai_engine.models.debugger.test_parser import TestParser
from ai_engine.models.debugger.patch_manager import PatchManager
from ai_engine.models.debugger.learning_db import LearningDB
from ai_engine.models.debugger.rollback_manager import RollbackManager
from ai_engine.models.debugger.debugger_reporter import DebuggerReporter
from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy

logger = logging.getLogger("DebuggerCore")
logger.setLevel(logging.DEBUG)


class DebuggerCore:
    """
    Main controller for the debugging system.
    Handles both simple and advanced debugging modes.
    """

    MAX_ATTEMPTS = 3

    def __init__(self, debug_strategy: Optional[DebuggingStrategy] = None):
        self.mode = "advanced" if debug_strategy else "simple"
        self.debug_strategy = debug_strategy

        # Modular Components
        self.test_runner = TestRunner()
        self.test_parser = TestParser()
        self.patch_manager = PatchManager(debug_strategy)
        self.learning_db = LearningDB()
        self.rollback_manager = RollbackManager()
        self.report_manager = ReportManager()

    def debug(self, max_retries: int = 3):
        """
        Entry point for debugging session.
        """
        if self.mode == "simple":
            return self._debug_simple(max_retries)
        else:
            return self._debug_advanced()

    def _debug_simple(self, max_retries: int = 3):
        """
        Runs debugging in simple mode.
        """
        logger.info("🚀 Running simple debugging mode...")

        for attempt in range(1, max_retries + 1):
            test_output = self.test_runner.run_tests_simple()
            failures = self.test_parser.parse_simple_failures(test_output)

            if not failures:
                return {"status": "success", "message": "All tests passed!"}

            for failure in failures:
                fix_success = self.patch_manager.apply_fix(failure)
                self.report_manager.log_attempt(failure, fix_success)

                if not fix_success:
                    self.rollback_manager.rollback(failure["file"])
                    return {"status": "error", "message": f"Could not fix {failure['file']} automatically."}

        return {"status": "error", "message": "Max retries reached. Debugging failed."}

    def _debug_advanced(self):
        """
        Runs debugging in advanced mode with a learning database.
        """
        logger.info("🚀 Running advanced debugging mode...")

        errors = self.test_runner.run_tests_advanced()
        if not errors:
            return {"status": "success", "message": "All tests passed!"}

        for err in errors:
            error_sig = self.learning_db.get_signature(err)
            patch = self.learning_db.get_known_fix(error_sig) or self.patch_manager.generate_patch(err)

            if not patch:
                logger.error("No patch generated for error: %s", err["error_message"])
                continue

            success = self.patch_manager.apply_patch(patch)
            self.learning_db.update(error_sig, patch, success)

            if success and self.test_runner.re_run_tests():
                return {"status": "success", "message": "Patch successfully applied!"}

        return {"status": "error", "message": "Advanced debugging failed."}
