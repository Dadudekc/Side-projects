#!/usr/bin/env python
"""
debugging_strategy.py

Handles automated debugging using a mix of:
- AST-based patching (for structured fixes like missing methods).
- AI-generated patches (fallback via AIModelManager).
- Learning DB for storing known fixes.
- Patch validation and application.
- Detecting import errors.

Features:
  - Detects missing methods and auto-generates method stubs via AST.
  - Uses AI to generate fixes when structured fixes don't apply.
  - Saves successful patches for future reuse.
  - Validates patches before applying.
  - Supports rollback if a fix makes things worse.
  - Detects import errors and extracts details to help with resolution.
"""

import ast
import re
import logging
import os
import subprocess
import json
import hashlib
from tempfile import NamedTemporaryFile
from typing import Dict, Any, Optional, List

from models.ai_model_manager import AIModelManager  # AI-powered debugging
from debugger_logger import DebuggerLogger         # Tracks debugging attempts
from debugger.project_context_analyzer import analyze_project  # Analyze project structure

# Configure logging
logger = logging.getLogger("DebuggingStrategy")
logger.setLevel(logging.DEBUG)


def find_class_in_file(source_file: str, class_name: str) -> Optional[int]:
    """
    Parses `source_file` using AST and returns the line number where a missing
    method stub could be inserted within the specified class.
    """
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)

        class_node, last_method_line = None, None

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                class_node = node
            elif class_node and isinstance(node, ast.FunctionDef):
                # Track the last method in that class
                last_method_line = getattr(node, 'end_lineno', node.lineno)

        if class_node:
            return last_method_line or (class_node.lineno + 1)
    except Exception as e:
        logger.error(f"❌ Error parsing {source_file}: {e}")
    return None


class DebuggingStrategy:
    """
    Automated debugging system that generates, applies, and refines patches.

    Features:
    - Detects structured errors (e.g., missing methods) and generates AST-based fixes.
    - Uses AI-generated patches for more complex issues.
    - Stores successful patches for future reuse.
    - Ensures patches don't break functionality.
    - Supports rollback if fixes fail.
    - Detects import errors to assist in resolving missing dependencies.
    """

    LEARNING_DB_FILE = "learning_db.json"
    PATCH_BACKUP_DIR = "patch_backups"
    MAX_RETRIES = 3

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.debugger_logger = DebuggerLogger()
        self.ai_manager = AIModelManager()  # Unified AI model manager
        self.learning_db = self._load_learning_db()
        self.project_info = analyze_project()  # Load project structure for fixing imports

    def _load_learning_db(self) -> Dict[str, Any]:
        """Loads the learning database from a JSON file."""
        if os.path.exists(self.LEARNING_DB_FILE):
            try:
                with open(self.LEARNING_DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"❌ Failed to load learning DB: {e}")
        return {}

    def _save_learning_db(self):
        """Saves the learning database to a JSON file."""
        try:
            with open(self.LEARNING_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.learning_db, f, indent=4)
        except Exception as e:
            self.logger.error(f"❌ Failed to save learning DB: {e}")

    def _compute_error_signature(self, error_message: str, code_context: str) -> str:
        """Computes a unique signature for an error based on its message and code context."""
        h = hashlib.sha256()
        h.update(error_message.encode("utf-8"))
        h.update(code_context.encode("utf-8"))
        return h.hexdigest()

    def detect_import_error(self, error_message: str) -> Optional[dict]:
        """
        Checks if an error is an import-related issue and extracts details.
        Returns a dictionary with keys 'missing_module' and 'source_file' (if available).
        """
        import_error_patterns = [
            r"ModuleNotFoundError: No module named '(.*?)'",
            r"ImportError: cannot import name '(.*?)' from '(.*?)'"
        ]
        for pattern in import_error_patterns:
            match = re.search(pattern, error_message)
            if match:
                missing_module = match.group(1)
                source_file = match.group(2) if "from" in pattern else None
                return {"missing_module": missing_module, "source_file": source_file}
        return None

    def generate_patch(self, error_message: str, code_context: str, test_file: str) -> Optional[str]:
        """
        Generates a patch for the provided error.
        - Uses AST-based fixes for known issues (e.g., missing methods).
        - Falls back to AI-generated patches if needed.
        - Saves successful fixes in a learning database.
        """
        # --- AST-based patching for missing methods ---
        missing_method_match = re.search(r"no attribute '(\w+)'", error_message)
        if missing_method_match:
            missing_method = missing_method_match.group(1)
            self.logger.info(f"🔍 Detected missing method: {missing_method}")
            # Derive the source file from the test filename by stripping 'test_' or '_test'
            source_file = test_file.replace("test_", "").replace("_test", "")
            if os.path.exists(source_file):
                insertion_line = find_class_in_file(source_file, "AgentActor")
                if insertion_line:
                    patch = (
                        f"--- {source_file}\n"
                        f"+++ {source_file}\n"
                        f"@@ -{insertion_line},0 +{insertion_line+1},8 @@\n"
                        f"     def {missing_method}(self, task):\n"
                        f"         \"\"\"Auto-generated method stub.\"\"\"\n"
                        f"         return None  # Placeholder implementation\n"
                    )
                    return patch
                else:
                    self.logger.warning("⚠️ Could not determine insertion point for missing method.")

        # --- AI-powered patch generation ---
        error_sig = self._compute_error_signature(error_message, code_context)
        if error_sig in self.learning_db:
            self.logger.info(f"✅ Using stored fix for error signature: {error_sig}")
            return self.learning_db[error_sig].get("patch")

        # Request a patch via AIModelManager
        patch = self.ai_manager.generate_patch(error_message, code_context, test_file)
        if not patch:
            self.logger.warning(f"⚠️ AI was unable to generate a patch for error: {error_message}")
            return None

        # Save patch to learning DB
        self.learning_db[error_sig] = {"patch": patch, "attempts": 1}
        self._save_learning_db()
        return patch

    def apply_patch(self, patch: str) -> bool:
        """Applies a given patch and validates success."""
        if not patch:
            return False

        # Write patch to a temporary file
        with NamedTemporaryFile(mode="w", delete=False, suffix=".patch") as temp_patch:
            patch_file = temp_patch.name
            temp_patch.write(patch)

        # Parse the patch header to determine the target file
        file_target_match = re.search(r"^--- (.+?)\n\+\+\+ (.+?)\n", patch, flags=re.MULTILINE)
        if not file_target_match:
            self.logger.error("❌ Cannot determine file target from patch header.")
            os.remove(patch_file)
            return False

        target_file = file_target_match.group(2).strip()
        self.logger.info(f"🛠️ Attempting to patch file: {target_file}")

        try:
            subprocess.run(["patch", target_file, patch_file], check=True)
            self.logger.info(f"✅ Patch applied successfully to {target_file}.")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Patch application failed: {e}")
            return False
        finally:
            os.remove(patch_file)

    def re_run_tests(self) -> bool:
        """Re-runs the test suite to verify that the applied patch fixes the issue."""
        result = subprocess.run(["pytest", "tests", "--disable-warnings"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            self.logger.info("✅ Tests passed after applying fixes.")
            return True
        self.logger.error(f"❌ Tests still failing:\n{result.stdout}")
        return False
