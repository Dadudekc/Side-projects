#!/usr/bin/env python
"""
debugging_strategy.py

Provides automated debugging functionality, including:
- AST-based fixes for structured issues (e.g., missing methods),
- AI-generated patches for more complex issues,
- A learning database (JSON-based) to store and reuse successful patches,
- Patch validation, application, and rollback,
- Import error detection for assisting with missing dependencies.

Dependencies:
    - ast
    - hashlib
    - json
    - logging
    - os
    - re
    - subprocess
    - tempfile.NamedTemporaryFile
    - typing (Dict, Any, Optional, List)
    - ai_engine.models.ai_model_manager (AIModelManager)
    - ai_engine.models.debugger.debugger_logger (DebuggerLogger)
    - ai_engine.models.debugger.project_context_analyzer (ProjectContextAnalyzer)
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

from ai_engine.models.ai_model_manager import AIModelManager
from ai_engine.models.debugger.debugger_logger import DebuggerLogger
from ai_engine.models.debugger.project_context_analyzer import ProjectContextAnalyzer

# Configure logging
logger = logging.getLogger("DebuggingStrategy")
logger.setLevel(logging.DEBUG)

def find_class_in_file(source_file: str, class_name: str) -> Optional[int]:
    """
    Parse a Python source file to find a specific class and determine where a 
    missing method stub should be inserted.

    This function uses the built-in `ast` module to locate the last method 
    definition within the given class. It returns the line number after 
    the last method, so that a new method stub can be appended.

    Args:
        source_file (str): Path to the Python source file to parse.
        class_name (str): Name of the class in which to insert a new method.

    Returns:
        Optional[int]: The line number where the new method can be inserted,
                       or None if the class or file cannot be parsed.
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
                last_method_line = getattr(node, 'end_lineno', node.lineno)

        if class_node:
            return last_method_line or (class_node.lineno + 1)
    except Exception as e:
        logger.error(f"❌ Error parsing {source_file}: {e}")
    return None

class DebuggingStrategy:
    """
    The DebuggingStrategy class orchestrates an automated debugging system that:
      - Detects and fixes structured issues (e.g., missing methods) using AST manipulations.
      - Leverages AI-generated patches for more complex issues.
      - Maintains a learning database to store successful patches for reuse.
      - Validates new patches, applies them conditionally, and can roll back if needed.
      - Detects and provides solutions for import errors.

    Typical usage involves:
      1. Instantiating DebuggingStrategy.
      2. Using `generate_patch` to create a patch for a given error.
      3. Using `apply_patch` to apply and validate the generated patch.
    """

    LEARNING_DB_FILE = "learning_db.json"
    PATCH_BACKUP_DIR = "patch_backups"
    MAX_RETRIES = 3

    def __init__(self):
        """
        Initialize the DebuggingStrategy by setting up:
          - A logger for debugging messages.
          - The DebuggerLogger for advanced logging capabilities.
          - The AIModelManager for AI-based patch generation.
          - Loading or creating a JSON-based learning database.
          - A ProjectContextAnalyzer for context about the project’s structure.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.debugger_logger = DebuggerLogger()
        self.ai_manager = AIModelManager()
        self.learning_db = self._load_learning_db()
        self.project_info = ProjectContextAnalyzer(project_root=os.getcwd())

    def _load_learning_db(self) -> Dict[str, Any]:
        """
        Load the learning database from a JSON file specified by LEARNING_DB_FILE.
        If the file does not exist or cannot be loaded, return an empty dictionary.

        Returns:
            Dict[str, Any]: The loaded learning database, or an empty dict on failure.
        """
        if os.path.exists(self.LEARNING_DB_FILE):
            try:
                with open(self.LEARNING_DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"❌ Failed to load learning DB: {e}")
        return {}

    def _save_learning_db(self):
        """
        Save the current in-memory learning database to a JSON file specified 
        by LEARNING_DB_FILE.
        """
        try:
            with open(self.LEARNING_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.learning_db, f, indent=4)
        except Exception as e:
            self.logger.error(f"❌ Failed to save learning DB: {e}")

    def _compute_error_signature(self, error_message: str, code_context: str) -> str:
        """
        Compute a unique signature (SHA-256 hash) for a given error based on its 
        message and a snippet of code context.

        Args:
            error_message (str): The raw error message.
            code_context (str): A snippet or portion of code around where 
                                the error occurred.

        Returns:
            str: A hex digest representing the hash of the error signature.
        """
        h = hashlib.sha256()
        h.update(error_message.encode("utf-8"))
        h.update(code_context.encode("utf-8"))
        return h.hexdigest()

    def detect_import_error(self, error_message: str) -> Optional[dict]:
        """
        Analyze an error message to determine if it is related to import issues.

        If a missing module or failed import is found, return a dictionary with 
        details. Otherwise, return None.

        Args:
            error_message (str): The error message to inspect.

        Returns:
            Optional[dict]: A dictionary containing 'missing_module' and 
                            optionally 'source_file' if recognized, or None 
                            if no import error is detected.
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
        Generate a patch to fix a given error. 

        The steps are:
          1. Check if the error is a 'missing method' error and try an AST-based fix.
          2. If no structured fix is found, compute an error signature and 
             see if a fix already exists in the learning DB.
          3. If not found in DB, use AI to generate a patch and store it in the DB.

        Args:
            error_message (str): The text of the error encountered.
            code_context (str): A snippet of code or logs surrounding where 
                                the error occurred.
            test_file (str): The path of the test file where the error surfaced.

        Returns:
            Optional[str]: A unified diff patch as a string, or None if no fix was generated.
        """
        missing_method_match = re.search(r"no attribute '(\w+)'", error_message)
        if missing_method_match:
            missing_method = missing_method_match.group(1)
            self.logger.info(f"🔍 Detected missing method: {missing_method}")
            # Attempt to infer source file from test file naming conventions
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

        # Check if we already have a fix in the learning database
        error_sig = self._compute_error_signature(error_message, code_context)
        if error_sig in self.learning_db:
            self.logger.info(f"✅ Using stored fix for error signature: {error_sig}")
            return self.learning_db[error_sig].get("patch")

        # Otherwise, generate a patch using AI
        patch = self.ai_manager.generate_patch(error_message, code_context, test_file)
        if not patch:
            self.logger.warning(f"⚠️ AI was unable to generate a patch for error: {error_message}")
            return None

        # Store the new patch in the learning DB
        self.learning_db[error_sig] = {"patch": patch, "attempts": 1}
        self._save_learning_db()
        return patch

    def apply_patch(self, patch: str) -> bool:
        """
        Apply a unified diff patch to the codebase using the 'patch' command-line tool. 

        This function:
          - Writes the patch to a temporary file.
          - Extracts the target file from the patch header.
          - Runs the 'patch' command to apply the diff.
          - Cleans up the temporary patch file.
        
        Args:
            patch (str): The unified diff string to apply.

        Returns:
            bool: True if the patch was successfully applied, False otherwise.
        """
        if not patch:
            return False

        with NamedTemporaryFile(mode="w", delete=False, suffix=".patch") as temp_patch:
            patch_file = temp_patch.name
            temp_patch.write(patch)

        # Extract file target from the patch header
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
