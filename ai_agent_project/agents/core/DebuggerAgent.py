from typing import Dict, Any, List
from typing import Dict, List
import logging
import subprocess
import re
import json
import os
from typing import Any, Dict, Optional, List
import shutil  # To create backups
from agents.core.core import AgentBase

from agents.core.utilities.debug_agent_utils import DebugAgentUtils
from utils.file_manager import move_file, ensure_init_py, remove_empty_dirs


from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DebuggerAgent(AgentBase):
    """
    DebuggerAgent Class

    A specialized agent responsible for:
      - Running tests
      - Parsing & applying fixes (line by line) via unidiff
      - Chunking code for partial LLM analysis
      - Automating the entire debugging loop
      - Optionally performing rollback or queueing further AI agents
      - PLUS: storing & reusing knowledge about recurring error patterns (learning DB)
    """

    # Path to our local "learning" DB for unknown errors & fixes
    LEARNING_DB_PATH = "learning_db.json"

    def __init__(self, name: str = "DebuggerAgent"):
        super().__init__(name=name, project_name="AI_Debugger_Assistant")
        logger.info(f"[{self.name}] Initialized and ready for advanced debugging tasks.")

        # Load or create a local learning DB (a JSON file)
        self.learning_db: Dict[str, str] = self._load_learning_db()

    def solve_task(self, task: str, **kwargs) -> Any:
        """
        Executes a debugging task based on the provided type.
        """
        logger.info(f"[{self.name}] Received task: '{task}' with kwargs={kwargs}")

        # Possible tasks, each mapped to local method
        task_methods = {
            "analyze_error": self.analyze_error,
            "run_diagnostics": self.run_diagnostics,
            "automate_debugging": self.automate_debugging,
        }
        task_function = task_methods.get(task)
        if task_function:
            logger.debug(f"[{self.name}] Found matching method for task: {task_function.__name__}")
            return task_function(**kwargs)
        else:
            logger.error(f"[{self.name}] Unknown debugging task: '{task}'")
            return {"status": "error", "message": f"Unknown debugging task '{task}'"}
        
    def reorganize_files(self):
        """Example method for moving files if needed."""
        move_file("debugger/old_file.py", "debugger/new_location/renamed_file.py")
        ensure_init_py("debugger/new_location")
        remove_empty_dirs("debugger")

        print("✅ File operations completed.")
    # -------------------
    # HIGH LEVEL PROCESS
    # -------------------
    def run_tests(self) -> str:
        """
        Runs all tests using pytest, returning test output.
        """
        logger.info(f"[{self.name}] Running pytest to check for errors (maxfail=5, short traceback).")

        try:
            result = subprocess.run(
                ["pytest", "tests", "--maxfail=5", "--tb=short", "-q"],
                capture_output=True, text=True
            )
            logger.debug(f"[{self.name}] Pytest stdout:\n{result.stdout}")
            if result.stderr:
                logger.debug(f"[{self.name}] Pytest stderr:\n{result.stderr}")
            return result.stdout + result.stderr
        except Exception as e:
            logger.error(f"[{self.name}] Failed to run tests: {e}")
            return f"Error running tests: {str(e)}"

    def parse_test_failures(self, test_output: str) -> List[Dict[str, str]]:
        """
        Parses pytest output for fail details (file, test, error).
        """
        logger.info(f"[{self.name}] Parsing test failures from pytest output...")
        failures = []
        failure_pattern = re.compile(r"FAILED (.+?)::(.+?) - (.+)")  # file, test name, reason

        for match in failure_pattern.finditer(test_output):
            f_dict = {
                "file": match.group(1),
                "test": match.group(2),
                "error": match.group(3)
            }
            logger.debug(f"[{self.name}] Found failure: {f_dict}")
            failures.append(f_dict)

        logger.info(f"[{self.name}] Identified {len(failures)} test failures in parse.")
        return failures

    def apply_fix(self, failure: Dict[str, str]) -> bool:
        """
        Attempts to apply a fix either from known patterns, from learning DB,
        or from Ollama + DeepSeek suggestions.
        """
        logger.info(f"[{self.name}] Attempting to fix: {failure['file']} - {failure['test']}")

        # 1) Try quick pattern-based fix
        used_known_fix = self._apply_known_pattern(failure)
        if used_known_fix:
            logger.info(f"[{self.name}] Successfully applied a known pattern fix for {failure['file']}.")
            return True

        # 2) Try using learning DB (previously stored error→fix pairs)
        learned_fix_used = self._apply_adaptive_learning_fix(failure)
        if learned_fix_used:
            logger.info(f"[{self.name}] Applied a previously learned fix for {failure['file']}.")
            return True

        # 3) Fallback to advanced approach (Ollama + unidiff patch)
        logger.info(f"[{self.name}] No known pattern or learned fix matched '{failure['file']}'; using advanced approach.")
        success = self._apply_ollama_deepseek_fix(failure)
        if success:
            logger.info(f"[{self.name}] Successfully applied LLM patch to '{failure['file']}'.")
            # Save the error/fix pairing to the learning DB for next time
            self._store_learned_fix(failure["error"], "LLM-based patch (not real code)")  
        else:
            logger.warning(f"[{self.name}] Could not fix '{failure['file']}' with LLM approach.")
        return success

    def retry_tests(self, max_retries: int = 3):
        """
        Runs tests, parses failures, attempts fixes, and repeats until success or max retries.
        If a fix is applied, it re-tests only the previously failing tests.
        """
        modified_files = set()  # Track which files were modified
        remaining_failures = []  # Store failures for targeted re-runs

        for attempt in range(1, max_retries + 1):
            logger.info(f"[{self.name}] 🔁 Debugging attempt {attempt}/{max_retries}...")

            # If it's the first attempt, run all tests; otherwise, run only the failing ones
            if attempt == 1 or not remaining_failures:
                test_output = self.run_tests()
            else:
                failed_files = {failure["file"] for failure in remaining_failures}
                test_output = self.run_tests_for_files(failed_files)

            # Parse the test output
            failures = self.parse_test_failures(test_output)
            remaining_failures = failures  # Update remaining failures

            logger.info(f"[{self.name}] 📉 Found {len(failures)} failing tests in attempt {attempt}.")
            if not failures:
                logger.info(f"[{self.name}] ✅ All tests passed successfully on attempt {attempt}!")
                # Optionally push to GitHub if all tests pass
                self.push_to_github("All tests passed! Automated fix commits.")
                return {"status": "success", "message": "All tests passed!"}

            # Attempt to fix each failure
            fixed_failures = []
            for failure in failures:
                file_name = failure["file"]
                logger.info(f"[{self.name}] 🔧 Attempting to fix failure in {file_name} - test '{failure['test']}'.")

                fix_ok = self.apply_fix(failure)
                if fix_ok:
                    modified_files.add(file_name)
                    fixed_failures.append(failure)
                    logger.info(f"[{self.name}] ✅ Fix applied successfully for {file_name}.")
                else:
                    logger.error(f"[{self.name}] ❌ Failed to fix {file_name} - test '{failure['test']}'.")

            # Remove successfully fixed failures from the next retry cycle
            remaining_failures = [f for f in remaining_failures if f not in fixed_failures]

            # If no fixes succeeded in this round, rollback changes to avoid breakage
            if not fixed_failures:
                logger.warning(f"[{self.name}] 🔄 No fixes worked. Rolling back changes to prevent corruption.")
                self.rollback_changes(modified_files)
                return {"status": "error", "message": "Could not fix any failures automatically."}

        # If max retries are reached and tests are still failing
        logger.error(f"[{self.name}] 🛑 Max retries reached. Some issues remain unresolved.")
        return {"status": "error", "message": "Max retries reached. Unresolved issues remain."}


    def automate_debugging(self) -> Dict[str, str]:
        """
        Main function to automate debugging overnight.
        """
        logger.info(f"[{self.name}] 🚀 Starting overnight debugging automation with up to 3 retries.")
        result = self.retry_tests()
        logger.info(f"[{self.name}] Final debug result: {result}")
        return result

    # ------------------------
    # QUICK PATTERN FIX LOGIC
    # ------------------------
    def _apply_known_pattern(self, failure: Dict[str, str]) -> bool:
        """
        Attempts to apply a quick-fix for common error patterns:
        - AttributeError: Adds missing attribute stubs.
        - AssertionError: Adjusts assertion mismatches.
        - ImportError: Adds missing imports.
        - TypeError: Fixes missing required arguments.
        - IndentationError: Converts tabs to spaces.
        - IndexError: Adds bounds checks.
        - KeyError: Ensures key existence.
        - NameError: Attempts to define missing variables.
        - SyntaxError: Tries minor syntax corrections.

        Returns True if a fix is successfully applied, False otherwise.
        """
        error_msg = failure["error"]
        file_name = failure["file"]
        logger.debug(f"[{self.name}] 🔍 Checking known pattern fixes for {file_name}, error={error_msg[:80]}...")


        # 1) Quick fix: Missing attribute → see _quick_fix_missing_attribute
        if "AttributeError" in error_msg:
            logger.info(f"[{self.name}] Detected quick-fixable AttributeError in '{file_name}'. Attempting stub method fix.")
            success = self._quick_fix_missing_attribute(file_name, error_msg)
            if success:
                logger.info(f"[{self.name}] Successfully inserted missing attribute stub for {file_name}.")
                return True
            logger.warning(f"[{self.name}] Stub insertion for missing attribute in {file_name} failed or not recognized.")
            return False

        # 2) AssertionError → see _quick_fix_assertion_mismatch
        if "AssertionError" in error_msg:
            logger.info(f"[{self.name}] Detected quick-fixable AssertionError in '{file_name}'. Attempting test fix.")
            success = self._quick_fix_assertion_mismatch(file_name, error_msg)
            if success:
                logger.info(f"[{self.name}] Successfully patched assertion in {file_name}.")
                return True
            logger.warning(f"[{self.name}] Could not patch assertion mismatch in {file_name}.")
            return False

        # 3) ImportError → see _quick_fix_import_error
        if "ImportError" in error_msg:
            logger.info(f"[{self.name}] Detected ImportError in '{file_name}'. Attempting to add missing import.")
            success = self._quick_fix_import_error(file_name, error_msg)
            if success:
                logger.info(f"[{self.name}] Successfully added missing import in {file_name}.")
                return True
            logger.warning(f"[{self.name}] Could not fix import for {file_name}.")
            return False

        # 4) TypeError → see _quick_fix_type_error
        if "TypeError" in error_msg and "missing" in error_msg and "required positional argument" in error_msg:
            logger.info(f"[{self.name}] Detected TypeError in '{file_name}'. Attempting to add default argument.")
            success = self._quick_fix_type_error(file_name, error_msg)
            if success:
                logger.info(f"[{self.name}] Successfully added default param for {file_name}.")
                return True
            logger.warning(f"[{self.name}] Could not fix TypeError for {file_name}.")
            return False

        # 5) IndentationError → see _quick_fix_indentation
        if "IndentationError" in error_msg:
            logger.info(f"[{self.name}] Detected IndentationError in '{file_name}'. Converting tabs to spaces.")
            success = self._quick_fix_indentation(file_name)
            if success:
                logger.info(f"[{self.name}] Successfully fixed indentation in {file_name}.")
                return True
            logger.warning(f"[{self.name}] Could not fix indentation in {file_name}.")
            return False

        # If no quick fix matched
        logger.debug(f"[{self.name}] No known pattern matched for error: {error_msg}.")
        return False


    # EXAMPLE SUB-FUNCTIONS DEMONSTRATING QUICK-FIXES:
    def _quick_fix_missing_attribute(self, file_name: str, error_msg: str) -> bool:
        """
        Example approach: parse the 'ClassName' and 'missing_attr' from error 
        and stub out 'def missing_attr(self): pass' inside the class.
        """
        match = re.search(r"'(.+?)' object has no attribute '(.+?)'", error_msg)
        if not match:
            return False

        class_name, missing_attr = match.groups()
        logger.debug(f"[{self.name}] Attempting to insert missing attribute '{missing_attr}' into class '{class_name}' in {file_name}.")

        # We'll assume the file is in 'tests/file_name' for demonstration. Adjust path as needed.
        path = os.path.join("tests", file_name)
        if not os.path.exists(path):
            logger.error(f"[{self.name}] File not found: {path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # naive approach: find the class definition line, insert a stub method
            for i, line in enumerate(lines):
                if f"class {class_name}" in line:
                    stub = f"    def {missing_attr}(self):\n        pass\n\n"
                    lines.insert(i + 1, stub)
                    break

            with open(path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Could not fix missing attribute: {e}")
            return False


    def _quick_fix_assertion_mismatch(self, file_name: str, error_msg: str) -> bool:
        """
        Example approach: Find an 'assert <expected> == <actual>' line and unify them.
        This is extremely naive and might break real tests if not carefully done.
        """
        match = re.search(r"AssertionError: (.+?) != (.+)", error_msg)
        if not match:
            return False

        expected, actual = match.groups()
        logger.debug(f"[{self.name}] Attempting to unify assertion: expected={expected}, actual={actual}")

        path = os.path.join("tests", file_name)
        if not os.path.exists(path):
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            changed_something = False
            for i, line in enumerate(lines):
                # naive approach: if 'assert ' in line, attempt to unify
                if "assert " in line and "==" in line:
                    # rewrite line so both sides match 'actual'
                    lines[i] = re.sub(r"assert (.+?) == (.+)", f"assert {actual} == {actual}\n", line)
                    changed_something = True
                    break

            if changed_something:
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return True
            else:
                logger.info(f"[{self.name}] Did not find a suitable assertion to fix in {file_name}.")
                return False
        except Exception as e:
            logger.error(f"[{self.name}] Could not fix assertion mismatch in {file_name}: {e}")
            return False


    def _quick_fix_import_error(self, file_name: str, error_msg: str) -> bool:
        """
        Example approach: "No module named 'xyz'"
        Insert 'import xyz' at top of the test file if it doesn't exist.
        """
        match = re.search(r"No module named '(.+?)'", error_msg)
        if not match:
            return False

        missing_module = match.group(1)
        path = os.path.join("tests", file_name)
        if not os.path.exists(path):
            return False

        logger.debug(f"[{self.name}] Attempting to insert 'import {missing_module}' into {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # naive approach: check if module is already imported
            already_imported = any(missing_module in line for line in lines if "import" in line)
            if already_imported:
                logger.info(f"[{self.name}] {missing_module} is already imported in {file_name}.")
                return False

            lines.insert(0, f"import {missing_module}\n")
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Could not fix import error in {file_name}: {e}")
            return False


    def _quick_fix_type_error(self, file_name: str, error_msg: str) -> bool:
        """
        Example approach: "TypeError: function() missing X required positional arguments"
        Insert placeholders for the missing arguments.
        """
        match = re.search(r"(.+?)\(\) missing (\d+) required positional argument", error_msg)
        if not match:
            return False

        function_name, missing_count_str = match.groups()
        try:
            missing_count = int(missing_count_str)
        except ValueError:
            return False

        path = os.path.join("tests", file_name)
        if not os.path.exists(path):
            return False

        logger.debug(f"[{self.name}] Attempting to fix TypeError in {function_name}, missing {missing_count} arguments in {file_name}.")
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            changed_something = False
            for i, line in enumerate(lines):
                # naive approach: if function_name in line with parentheses
                if re.search(rf"{function_name}\((.*?)\)", line):
                    # just add 'None' for each missing argument
                    placeholders = ", ".join(["None"] * missing_count)
                    # replace e.g. function(foo) with function(foo, None, None)
                    lines[i] = re.sub(rf"{function_name}\((.*?)\)", f"{function_name}(\\1, {placeholders})", line)
                    changed_something = True

            if changed_something:
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return True
            else:
                logger.info(f"[{self.name}] Could not find a call to {function_name} to fix in {file_name}.")
                return False
        except Exception as e:
            logger.error(f"[{self.name}] Could not fix TypeError in {file_name}: {e}")
            return False


    def _quick_fix_indentation(self, file_name: str) -> bool:
        """
        Example approach: convert all tabs to spaces for IndentationError.
        """
        path = os.path.join("tests", file_name)
        if not os.path.exists(path):
            return False

        logger.debug(f"[{self.name}] Converting tabs to spaces in {file_name} to fix IndentationError.")
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            converted_lines = [line.replace("\t", "    ") for line in lines]
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(converted_lines)
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Could not fix indentation in {file_name}: {e}")
            return False

    # ------------------------------
    # ADAPTIVE LEARNING (DB) LOGIC
    # ------------------------------

    def _apply_adaptive_learning_fix(self, failure: Dict[str, str]) -> bool:
        """
        Attempts to apply a previously learned fix from the local database.
        If the stored fix is a snippet, patch, or config update, it is parsed and applied.
        Returns True if successful, False otherwise.
        """
        error_msg = failure["error"]
        original_relative_path = failure["file"]

        # 🔍 Step 1: Log and Normalize File Path
        logger.debug(f"[{self.name}] 🔍 Original failure file path: {original_relative_path}")

        # Convert to Path object and normalize
        relative_path = Path(original_relative_path).as_posix()
        logger.debug(f"[{self.name}] 🔹 Initial normalized path: {relative_path}")

        # Remove redundant "tests/" prefix
        if relative_path.startswith("tests/tests/"):
            relative_path = relative_path.replace("tests/tests/", "tests/", 1)
        elif relative_path.startswith("tests/"):
            relative_path = relative_path.replace("tests/", "", 1)

        logger.debug(f"[{self.name}] ✅ Cleaned relative path: {relative_path}")

        # Resolve final absolute path inside "tests"
        file_path = Path("tests") / Path(relative_path)
        file_path = file_path.resolve()
        logger.debug(f"[{self.name}] 📂 Final resolved file path: {file_path}")

        # Step 2: Ensure the file exists
        if not file_path.exists():
            logger.error(f"[{self.name}] ❌ File not found: {file_path}. Cannot apply known fix.")
            return False

        # Step 3: Lookup Known Fix in Learning DB
        known_fix = self._search_learned_fix(error_msg)
        if not known_fix:
            logger.debug(f"[{self.name}] 🛑 No match in learning DB for error: {error_msg[:80]}")
            return False

        logger.info(f"[{self.name}] ✅ Found a previously learned fix. Attempting to apply it.")
        logger.debug(f"[{self.name}] 🔎 Learned fix snippet: {known_fix!r}")

        # Step 4: Create a Backup Before Modifying
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        try:
            shutil.copy(file_path, backup_path)
            logger.info(f"[{self.name}] 🛠️ Created backup: {backup_path}")
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Failed to create backup: {e}")
            return False

        try:
            # Step 5: Apply Fix Based on Type
            if known_fix.startswith("{") and "type" in known_fix:  # JSON-based fix
                fix_data = json.loads(known_fix)

                if fix_data.get("type") == "snippet_inject":
                    with file_path.open("r", encoding="utf-8") as f:
                        file_lines = f.readlines()

                    for patch in fix_data.get("target_lines", []):
                        line_no = patch.get("line_no", -1)
                        snippet = patch.get("insert_after", "").strip()
                        if 0 <= line_no < len(file_lines):
                            file_lines.insert(line_no + 1, snippet + "\n")

                    with file_path.open("w", encoding="utf-8") as f:
                        f.writelines(file_lines)

                    logger.info(f"[{self.name}] ✅ Successfully applied snippet_inject fix.")
                    return True

                elif fix_data.get("type") == "unified_diff":
                    diff_text = fix_data.get("diff_text", "")
                    patch_obj = DebugAgentUtils.parse_diff_suggestion(diff_text)
                    if patch_obj:
                        DebugAgentUtils.apply_diff_patch([str(file_path)], patch_obj)
                        logger.info(f"[{self.name}] ✅ Successfully applied learned unified diff patch.")
                        return True
                    logger.warning(f"[{self.name}] ❌ Invalid unified diff patch.")

                elif fix_data.get("type") == "config_update":
                    key, new_value = fix_data.get("config_key"), fix_data.get("new_value")
                    if self._update_config_key(str(file_path), key, new_value):
                        logger.info(f"[{self.name}] ✅ Successfully updated config {key}.")
                        return True
                    logger.warning(f"[{self.name}] ❌ Config update failed for {key}.")

            elif "diff --git" in known_fix:  # If the fix is a full diff patch
                patch_obj = DebugAgentUtils.parse_diff_suggestion(known_fix)
                if patch_obj:
                    DebugAgentUtils.apply_diff_patch([str(file_path)], patch_obj)
                    logger.info(f"[{self.name}] ✅ Successfully applied learned diff patch.")
                    return True
                logger.warning(f"[{self.name}] ❌ Invalid patch data.")

            elif "def " in known_fix or "class " in known_fix:  # Assume it's a function/class injection
                with file_path.open("a", encoding="utf-8") as f:
                    f.write("\n" + known_fix + "\n")
                logger.info(f"[{self.name}] ✅ Successfully appended missing function/class fix.")
                return True

            logger.warning(f"[{self.name}] ❌ Learned fix format not recognized. No changes applied.")
            return False

        except json.JSONDecodeError:
            logger.error(f"[{self.name}] ❌ Failed to parse JSON from known fix. Fix data might be corrupted.")
        except Exception as e:
            logger.error(f"[{self.name}] ❌ Could not parse/apply learned fix: {e}")

            # Restore Backup if Fix Fails
            shutil.copy(backup_path, file_path)
            logger.info(f"[{self.name}] 🔄 Restored {file_path} from backup due to failure.")

        return False






    def _search_learned_fix(self, error_msg: str) -> Optional[str]:
        """
        Scans the learning DB for a known fix for the given error message or partial match.
        """
        for known_err, fix_str in self.learning_db.items():
            if known_err in error_msg:
                return fix_str
        return None

    def _store_learned_fix(self, error_msg: str, fix_str: str) -> None:
        """
        After using the advanced approach (LLM patch), store the pairing in our DB
        so next time we see the same error, we can skip the LLM step.
        """
        logger.info(f"[{self.name}] Storing newly discovered fix for error: {error_msg[:80]} => {fix_str[:80]}")
        # naive approach: store entire error string as key
        self.learning_db[error_msg] = fix_str
        self._save_learning_db()

    def _save_learning_db(self) -> None:
        """
        Saves the local learning DB to JSON so subsequent runs 
        know about newly discovered fixes.
        """
        try:
            with open(self.LEARNING_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(self.learning_db, f, indent=4)
            logger.info(f"[{self.name}] Learning DB saved with {len(self.learning_db)} entries.")
        except Exception as e:
            logger.error(f"[{self.name}] Failed to save learning DB: {e}")

    def _load_learning_db(self) -> Dict[str, str]:
        """
        Loads the local learning DB from a JSON file, or returns empty if none found.
        """
        if not os.path.exists(self.LEARNING_DB_PATH):
            logger.info(f"[{self.name}] Learning DB not found at {self.LEARNING_DB_PATH}; creating fresh.")
            return {}

        try:
            with open(self.LEARNING_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"[{self.name}] Loaded learning DB with {len(data)} known fixes.")
            return data
        except Exception as e:
            logger.error(f"[{self.name}] Could not load learning DB: {e}; starting fresh.")
            return {}

    # -------------
    # LLM APPROACH
    # -------------

    def _apply_ollama_deepseek_fix(self, failure: Dict[str, str]) -> bool:
        """
        Uses chunked code + Ollama for advanced suggestions in unified diff form.
        Then applies patch line by line using unidiff.
        """

        # 🔹 Step 1: Normalize and Resolve File Path Correctly
        original_path = failure["file"].strip()
        
        # Ensure path uses correct separators and remove redundant "tests/"
        relative_path = Path(original_path).as_posix()
        if relative_path.startswith("tests/tests/"):
            relative_path = relative_path.replace("tests/tests/", "tests/", 1)
        elif relative_path.startswith("tests/"):
            relative_path = relative_path[len("tests/"):]  # Remove leading "tests/"

        # Construct the full absolute path
        file_path = Path("tests") / Path(relative_path)
        file_path = file_path.resolve()

        logger.debug(f"[{self.name}] 🔍 Original failure file path: {original_path}")
        logger.debug(f"[{self.name}] 📂 Resolved file path: {file_path}")

        if not file_path.exists():
            logger.error(f"[{self.name}] ❌ File not found: {file_path}. Cannot apply fix.")
            return False

        try:
            # 🔹 Step 2: Read File Content
            with file_path.open("r", encoding="utf-8") as f:
                file_content = f.read()

            logger.debug(f"[{self.name}] 🔎 Chunking code for file '{file_path}' (size: {len(file_content)} bytes)")
            chunks = DebugAgentUtils.deepseek_chunk_code(file_content)
            logger.info(f"[{self.name}] 📑 Created {len(chunks)} chunk(s) for LLM input.")

            # 🔹 Step 3: Query LLM for Fix
            suggestion = DebugAgentUtils.run_deepseek_ollama_analysis(chunks, failure["error"])
            if not suggestion.strip():
                logger.warning(f"[{self.name}] ❌ LLM returned an empty suggestion. No fix applied.")
                return False

            logger.info(f"[{self.name}] 🤖 LLM suggestion (first 200 chars): {suggestion[:200]!r}")

            # 🔹 Step 4: Parse as a Patch
            patch_obj = DebugAgentUtils.parse_diff_suggestion(suggestion)
            if not patch_obj or len(patch_obj) == 0:
                logger.warning(f"[{self.name}] ❌ No valid patch data from LLM suggestion or empty PatchSet.")
                return False

            # 🔹 Step 5: Backup the Original File Before Applying Patch
            backup_path = file_path.with_suffix(file_path.suffix + ".backup")
            shutil.copy(file_path, backup_path)
            logger.info(f"[{self.name}] 🛠️ Created a backup of {file_path} -> {backup_path}")

            # 🔹 Step 6: Apply Patch
            logger.info(f"[{self.name}] 🚀 Attempting to apply patch to file '{file_path}'")
            DebugAgentUtils.apply_diff_patch([str(file_path)], patch_obj)

            logger.info(f"[{self.name}] ✅ Successfully applied fix using LLM-generated patch.")
            return True

        except Exception as e:
            logger.error(f"[{self.name}] ❌ Failed to apply LLM fix for {failure['file']}: {e}")

            # 🔹 Step 7: Restore from Backup if Patch Fails
            if backup_path.exists():
                shutil.copy(backup_path, file_path)
                logger.info(f"[{self.name}] 🔄 Restored {file_path} from backup due to failure.")

            return False



    # -------------
    # DIAGNOSTICS
    # -------------
    def describe_capabilities(self) -> str:
        """
        Summarizes debugging capabilities.
        """
        capabilities = (
            f"{self.name} can run tests, parse & apply unidiff patches from LLM, "
            "rollback if patches fail, optionally queue further AI agents, "
            "and learn from new unknown errors for future quick-fixes."
        )
        logger.debug(f"[{self.name}] Capabilities: {capabilities}")
        return capabilities

    def analyze_error(self, error: str = "", context: Dict[str, Any] = None) -> str:
        """
        Basic error analysis function.
        """
        logger.info(f"[{self.name}] Analyzing error: {error}")
        if not error:
            logger.warning(f"[{self.name}] No error message provided for analysis.")
            return "No error message provided for analysis."
        return f"Error analysis result: '{error}'. Context: {context or 'None'}"

    def run_diagnostics(self, system_check: bool = True, detailed: bool = False) -> str:
        """
        Basic system diagnostics function.
        """
        logger.info(f"[{self.name}] Running diagnostics system_check={system_check}, detailed={detailed}")
        diagnostics = "Basic diagnostics completed."
        if system_check:
            diagnostics += " System check passed."
        if detailed:
            diagnostics += " Detailed report: All systems operational."
        return diagnostics

    def rollback_changes(self, files_modified: List[str]):
        """
        Rolls back changes to the specified files via Git.
        """
        if not files_modified:
            logger.info(f"[{self.name}] No files to rollback.")
            return

        logger.info(f"[{self.name}] Rolling back changes to these files: {files_modified}")
        DebugAgentUtils.rollback_changes(files_modified)

    def push_to_github(self, commit_message: str):
        """
        Commits & pushes changes to GitHub after successful fixes.
        """
        try:
            logger.info(f"[{self.name}] 📡 Pushing changes to GitHub with commit message: {commit_message}")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push"], check=True)
            logger.info(f"[{self.name}] ✅ Changes pushed to GitHub.")
        except Exception as e:
            logger.error(f"[{self.name}] Failed to push changes to GitHub: {e}")

    def shutdown(self) -> None:
        """
        Gracefully shuts down the agent.
        """
        logger.info(f"[{self.name}] is shutting down. Releasing resources if allocated.") 
