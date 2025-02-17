import os
import shutil
from pathlib import Path

# Define the correct structure
PROJECT_ROOT = Path.cwd()  # Ensure you run this script from ai_agent_project
STRUCTURE = {
    "agents": ["AgentActor.py", "AgentDispatcher.py", "custom_agent.py", "debugger_agent.py"],
    "agents/core": [
        "agent_dispatcher.py", "agent_registry.py", "AgentBase.py", "DebuggerAgent.py",
        "DeepSeekModel.py", "gpt_forecasting.py", "graph_memory.py", "JournalAgent.py",
        "logger.py", "memory_engine.py", "professor_synapse_agent.py", "trading_agent.py"
    ],
    "agents/core/utilities": [
        "AgentBase.py", "ai_agent_utils.py", "ai_client.py", "ai_model_manager.py",
        "ai_patch_utils.py", "CustomAgent.py", "debug_agent_utils.py"
    ],
    "ai_engine/models": ["ai_model_manager.py", "deepseek_model.py", "mistral_model.py", "openai_model.py"],
    "ai_engine/models/debugger": [
        "ai_patch_retry_manager.py", "auto_fix_manager.py", "auto_fixer.py",
        "debug_agent_auto_fixer.py", "debugger_cli.py", "debugger_core.py",
        "debugger_logger.py", "debugger_reporter.py", "debugger_runner.py",
        "debugging_strategy.py", "email_reporter.py", "error_parser.py",
        "learning_db.py", "patch_manager.py", "patch_tracking_manager.py",
        "project_context_analyzer.py", "rollback_manager.py", "test_parser.py",
        "test_runner.py"
    ],
    "ai_engine/models/memory": [
        "context_manager.py", "memory_manager.py", "performance_monitor.py",
        "structured_memory_segment.py", "vector_memory_manager.py"
    ],
    "scripts": ["run_debugger_agent.py", "run_debugger.py", "fix_imports.py", "fix_test_issues.py"],
    "tests": ["run_tests.py", "test_agent_base.py", "test_agent_dispatcher.py", "test_ai_model_manager.py"],
    "ui": ["debugger_dashboard.py"],
    "utils": [],
    "config": [],
    "logs": [],
    "backup": [],
}

# Directories to delete (cache files)
CACHE_DIRS = ["__pycache__", ".pytest_cache", "debugagent.egg-info", "reports_archive"]

def ensure_directories():
    """Create necessary directories if they don't exist."""
    for dir_path in STRUCTURE.keys():
        full_path = PROJECT_ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)

def move_files():
    """Move files to their correct directories."""
    for folder, files in STRUCTURE.items():
        for file_name in files:
            src = PROJECT_ROOT / file_name
            dest = PROJECT_ROOT / folder / file_name

            if src.exists():
                print(f"Moving {src} → {dest}")
                shutil.move(str(src), str(dest))

def remove_cache():
    """Delete unnecessary cache directories."""
    for cache in CACHE_DIRS:
        cache_path = PROJECT_ROOT / cache
        if cache_path.exists():
            print(f"Removing {cache_path}")
            shutil.rmtree(cache_path, ignore_errors=True)

def main():
    print("Ensuring directory structure...")
    ensure_directories()

    print("\nMoving files to correct locations...")
    move_files()

    print("\nCleaning up cache files...")
    remove_cache()

    print("\n✅ Project structure organized successfully!")

if __name__ == "__main__":
    main()
