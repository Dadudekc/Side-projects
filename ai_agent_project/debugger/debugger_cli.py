import argparse
import logging
import json
import os
from debugger_core import DebuggerCore
from patch_tracking_manager import PatchTrackingManager

# Configure CLI logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("DebuggerCLI")

# AI Performance Report File
AI_PERFORMANCE_FILE = "ai_performance.json"


def load_ai_performance():
    """Loads AI debugging performance report."""
    if os.path.exists(AI_PERFORMANCE_FILE):
        try:
            with open(AI_PERFORMANCE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error loading AI performance file: {e}")
    return {}


def show_ai_performance():
    """Displays AI debugging performance analytics."""
    performance_data = load_ai_performance()
    if not performance_data:
        logger.info("📊 No AI performance data available yet.")
        return

    logger.info("\n📈 **AI Debugging Performance Report** 📈")
    for date, stats in sorted(performance_data.items(), reverse=True):
        logger.info(f"\n📅 **Date:** {date}")
        logger.info(f"🔹 Total Fixes: {stats['total_fixes']}")
        logger.info(f"✅ Success Rate: {stats['success_rate']}%")
        logger.info(f"🛠️ AI Patch Quality Scores: {stats['ai_feedback']}")


def main():
    """
    CLI interface for DebuggerCore.
    """
    parser = argparse.ArgumentParser(description="Automated Debugging CLI")
    parser.add_argument("--debug", action="store_true", help="Run automated debugging process")
    parser.add_argument("--logs", action="store_true", help="Display previous debugging logs")
    parser.add_argument("--rollback", action="store_true", help="Rollback last attempted fixes")
    parser.add_argument("--performance", action="store_true", help="View AI debugging performance report")
    parser.add_argument("--fix-imports", action="store_true", help="Check and fix missing imports")
    parser.add_argument("--file", type=str, help="Debug a specific file")
    
    args = parser.parse_args()
    debugger = DebuggerCore()
    patch_tracker = PatchTrackingManager()

    if args.debug:
        if args.file:
            logger.info(f"🚀 Debugging Specific File: {args.file}...")
            result = debugger.debug_file(args.file)
        else:
            logger.info("🚀 Starting Full Automated Debugging Process...")
            result = debugger.debug()
        
        logger.info(f"🔍 Debugging Result: {result}")

    elif args.logs:
        logger.info("📜 Retrieving Debug Logs...\n")
        debugger.show_logs()

    elif args.rollback:
        logger.info("🔄 Rolling Back Last Attempted Fixes...")
        files_to_rollback = debugger.get_last_modified_files()
        if not files_to_rollback:
            logger.info("⚠️ No recent modifications detected.")
        else:
            debugger.rollback_changes(files_to_rollback)

    elif args.performance:
        show_ai_performance()

    elif args.fix_imports:
        logger.info("🔍 Scanning for Import Errors...")
        import_fixes = patch_tracker.import_fixes
        if not import_fixes:
            logger.info("✅ No import errors detected.")
        else:
            logger.info("\n📌 **Import Fix Statistics:**")
            for module, data in import_fixes.items():
                logger.info(f"📦 **Module:** {module} | ✅ Fixed: {data['fixed']} | ❌ Failed: {data['failed']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
