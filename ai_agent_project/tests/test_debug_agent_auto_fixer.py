"""
test_debug_agent_auto_fixer.py

Test suite for DebugAgentAutoFixer and PatchTrackingManager.

Key Tests:
- Module existence enforcement
- Fixing import issues in test files
- Detecting and fixing unterminated strings
- Detecting syntax errors
- Backup and restore functionality
- Re-attempting failed patches before AI intervention

Updates:
- More detailed docstrings
- Ensures tests do not permanently wipe files
- Leverages fixture-based cleanup to remove artifacts
"""

import json
import os
import shutil
import pytest

from ai_engine.models.debugger.debug_agent_auto_fixer import DebugAgentAutoFixer
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager

# Project Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AGENTS_CORE_PATH = os.path.join(PROJECT_ROOT, "..", "agents", "core")
TESTS_PATH = os.path.join(PROJECT_ROOT, "..", "tests")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "..", "rollback_backups")

# Required Modules
REQUIRED_MODULES = [
    "AIConfidenceManager",
    "AIPatchOptimizer",
    "AIPatchRetryManager",
    "AIPatchReviewManager",
    "AIRollbackAnalysis",
    "AutoFixer",
    "DebuggerCLI",
    "DebuggerCore",
    "debugger_reporter",
    "debugger_runner",
    "debugging_strategy",
    "AutoFixManager",
]


@pytest.fixture
def auto_fixer():
    """
    Fixture to provide a fresh DebugAgentAutoFixer instance.
    If needed, you can pass `needed_files` to its constructor
    for selective copying from project_files -> test_workspace.
    """
    return DebugAgentAutoFixer()


@pytest.fixture(autouse=True)
def fix_function():
    """
    Ensures clean test runs by removing any test artifacts created 
    during each test (like newly created modules or backup dirs).
    """
    yield  # Run the actual test

    # Clean up all created modules
    for module in REQUIRED_MODULES:
        module_path = os.path.join(AGENTS_CORE_PATH, f"{module}.py")
        if os.path.exists(module_path):
            os.remove(module_path)

    # Clean up any rollback backups
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)


def test_ensure_modules_exist(auto_fixer):
    """Test if missing required modules are created successfully by auto_fixer."""
    auto_fixer.ensure_modules_exist()

    for module in REQUIRED_MODULES:
        module_path = os.path.join(AGENTS_CORE_PATH, f"{module}.py")
        assert os.path.exists(module_path), f"❌ {module} module was not created!"


def test_fix_test_imports(auto_fixer):
    """Test if auto_fixer can correct broken imports in test files."""
    test_file_path = os.path.join(TESTS_PATH, "test_dummy.py")

    # Create a dummy test file with broken imports
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("from agents.core.DebuggerCore import DebuggerCore\n")
        file.write("from agents.core.DebuggerCLI import DebuggerCLI\n")

    auto_fixer.fix_test_imports()

    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert "import DebuggerCore" in content, "❌ DebuggerCore import was not fixed!"
    assert "import DebuggerCLI" in content, "❌ DebuggerCLI import was not fixed!"

    os.remove(test_file_path)


def test_fix_unterminated_strings(auto_fixer):
    """Test if unterminated strings are correctly detected and fixed."""
    test_file_path = os.path.join(TESTS_PATH, "test_unterminated.py")

    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write('print("Hello World\n')  # Unterminated string

    auto_fixer.fix_unterminated_strings()

    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert content.endswith('")\n'), "❌ Unterminated string was not fixed!"
    os.remove(test_file_path)


def test_check_syntax_errors(auto_fixer):
    """Test if syntax errors are correctly identified by auto_fixer."""
    test_file_path = os.path.join(TESTS_PATH, "test_syntax_error.py")

    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("def bad_syntax(\n")  # Missing closing parenthesis

    # We expect auto_fixer.check_syntax_errors() to raise a SyntaxError
    with pytest.raises(SyntaxError):
        auto_fixer.check_syntax_errors()

    os.remove(test_file_path)


def test_backup_and_restore(auto_fixer):
    """Test if file backup and restore operations function correctly."""
    test_file_path = os.path.join(TESTS_PATH, "test_backup.py")

    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("original content")

    auto_fixer.backup_file(test_file_path)

    # Overwrite the file
    with open(test_file_path, "w", encoding="utf-8") as file:
        file.write("modified content")

    auto_fixer.restore_backup(test_file_path)

    with open(test_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    assert content == "original content", "❌ Backup restoration failed!"
    os.remove(test_file_path)


def test_re_attempt_failed_patches(auto_fixer):
    """Test if auto_fixer correctly retries failed patches before AI-based solutions."""
    patch_tracker = PatchTrackingManager()
    error_signature = "test_error_signature"
    file_path = os.path.join(TESTS_PATH, "test_patch.py")

    # Create a dummy failed patch
    failed_patch = "--- test_patch.py\n+++ test_patch.py\n- old_code\n+ fixed_code"

    # Record it as a failed patch
    patch_tracker.record_failed_patch(error_signature, failed_patch)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("old_code")

    success = auto_fixer.re_attempt_failed_patches(error_signature, file_path)
    assert success, "❌ Failed patch reattempt was unsuccessful!"

    os.remove(file_path)
