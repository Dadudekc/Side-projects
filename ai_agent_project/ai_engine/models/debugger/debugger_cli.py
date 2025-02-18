import os
import json
import argparse
import logging
from typing import Any, Dict, Optional

from ai_engine.models.debugger.debugger_core import DebugAgent
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("DebuggerCLI")

# AI Performance Report File
AI_PERFORMANCE_FILE = "ai_performance.json"


class DebuggerCLI:
    """
    Command-line interface for managing and executing debugging operations.
    """

    def __init__(self) -> None:
        """
        Initializes the DebuggerCLI with the necessary debugging components.
        """
        self.debugger_core: DebugAgent = DebugAgent()
        self.patch_tracker: PatchTrackingManager = PatchTrackingManager()

    def load_ai_performance(self) -> Dict[str, Any]:
        """
        Loads AI debugging performance report from a JSON file.

        Returns:
            A dictionary with the performance data if available; otherwise, an empty dict.
        """
        if os.path.exists(AI_PERFORMANCE_FILE):
            try:
                with open(AI_PERFORMANCE_FILE, "r", encoding="utf-8") as f:
                    performance_data = json.load(f)
                return performance_data
            except Exception as e:
                logger.error(f"❌ Error loading AI performance file: {e}")
        return {}

    def show_ai_performance(self) -> None:
        """
        Displays AI debugging performance analytics.
        """
        performance_data = self.load_ai_performance()
        if not performance_data:
            logger.info("📊 No AI performance data available yet.")
            return

        logger.info("\n📈 **AI Debugging Performance Report** 📈")
        for date, stats in sorted(performance_data.items(), reverse=True):
            logger.info(f"\n📅 **Date:** {date}")
            logger.info(f"🔹 Total Fixes: {stats.get('total_fixes', 'N/A')}")
            logger.info(f"✅ Success Rate: {stats.get('success_rate', 'N/A')}%")
            logger.info(f"🛠️ AI Patch Quality Scores: {stats.get('ai_feedback', 'N/A')}")

    def run_debugger(self, file: Optional[str] = None) -> None:
        """
        Runs the debugging process, either on a specific file or the entire project.

        Args:
            file: Optional; the path of a specific file to debug.
        """
        try:
            if file:
                logger.info(f"🚀 Debugging Specific File: {file}...")
                result = self.debugger_core.debug_file(file)
            else:
                logger.info("🚀 Starting Full Automated Debugging Process...")
                result = self.debugger_core.debug()
            logger.info(f"🔍 Debugging Result: {result}")
        except Exception as e:
            logger.error(f"❌ An error occurred during debugging: {e}")

    def show_logs(self) -> None:
        """
        Displays previous debugging logs.
        """
        try:
            logger.info("📜 Retrieving Debug Logs...\n")
            self.debugger_core.show_logs()
        except Exception as e:
            logger.error(f"❌ Failed to retrieve logs: {e}")

    def rollback_fixes(self) -> None:
        """
        Rolls back the last attempted fixes.
        """
        try:
            logger.info("🔄 Rolling Back Last Attempted Fixes...")
            files_to_rollback = self.debugger_core.get_last_modified_files()
            if not files_to_rollback:
                logger.info("⚠️ No recent modifications detected.")
            else:
                self.debugger_core.rollback_changes(files_to_rollback)
        except Exception as e:
            logger.error(f"❌ Failed to rollback fixes: {e}")

    def fix_imports(self) -> None:
        """
        Checks for and fixes missing imports.
        """
        try:
            logger.info("🔍 Scanning for Import Errors...")
            import_fixes = self.patch_tracker.import_fixes
            if not import_fixes:
                logger.info("✅ No import errors detected.")
            else:
                logger.info("\n📌 **Import Fix Statistics:**")
                for module, data in import_fixes.items():
                    fixed = data.get('fixed', 0)
                    failed = data.get('failed', 0)
                    logger.info(f"📦 **Module:** {module} | ✅ Fixed: {fixed} | ❌ Failed: {failed}")
        except Exception as e:
            logger.error(f"❌ An error occurred while fixing imports: {e}")

    def parse_arguments(self) -> argparse.Namespace:
        """
        Parses command-line arguments and returns the parsed arguments.

        Returns:
            An argparse.Namespace object with the parsed command-line arguments.
        """
        parser = argparse.ArgumentParser(description="Automated Debugging CLI")
        parser.add_argument("--debug", action="store_true", help="Run automated debugging process")
        parser.add_argument("--logs", action="store_true", help="Display previous debugging logs")
        parser.add_argument("--rollback", action="store_true", help="Rollback last attempted fixes")
        parser.add_argument("--performance", action="store_true", help="View AI debugging performance report")
        parser.add_argument("--fix-imports", action="store_true", help="Check and fix missing imports")
        parser.add_argument("--file", type=str, help="Debug a specific file")
        parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

        args = parser.parse_args()

        # Set logging level to DEBUG if verbose flag is provided
        if args.verbose:
            logger.setLevel(logging.DEBUG)
            logger.debug("Verbose mode enabled.")

        return args

    def execute_commands(self, args: argparse.Namespace) -> None:
        """
        Executes commands based on the provided command-line arguments.

        Args:
            args: Parsed command-line arguments.
        """
        if not any([args.debug, args.logs, args.rollback, args.performance, args.fix_imports]):
            logger.info("No command specified. Use --help for usage information.")
            return

        if args.debug:
            self.run_debugger(args.file)
        if args.logs:
            self.show_logs()
        if args.rollback:
            self.rollback_fixes()
        if args.performance:
            self.show_ai_performance()
        if args.fix_imports:
            self.fix_imports()


def main() -> None:
    cli = DebuggerCLI()
    args = cli.parse_arguments()
    cli.execute_commands(args)


if __name__ == "__main__":
    main()
