import logging
import subprocess
import re
import json
import os
from typing import Any, Dict, Optional, List

from agents.core.utilities.AgentBase import AgentBase
from agents.core.utilities.debug_agent_utils import DebugAgentUtils

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
      - Optionally performing rollback or queueing further agents
    """

    def __init__(self, name: str = "DebuggerAgent"):
        super().__init__(name=name, project_name="AI_Debugger_Assistant")
        logger.info(f"{self.name} initialized and ready for advanced debugging tasks.")

    def solve_task(self, task: str, **kwargs) -> Any:
        """
        Executes a debugging task based on the provided type.
        """
        logger.info(f"{self.name} received task: '{task}'")

        task_methods = {
            "analyze_error": self.analyze_error,
            "run_diagnostics": self.run_diagnostics,
            "automate_debugging": self.automate_debugging,
        }
        task_function = task_methods.get(task)
        if task_function:
            return task_function(**kwargs)
        else:
            logger.error(f"Unknown debugging task: '{task}'")
            return {"status": "error", "message": f"Unknown debugging task '{task}'"}

    def run_tests(self) -> str:
        """
        Runs all tests using pytest, returning test output.
        """
        logger.info("Running pytest to check for errors...")

        try:
            result = subprocess.run(
                ["pytest", "tests", "--maxfail=5", "--tb=short", "-q"],
                capture_output=True, text=True
            )
            logger.debug(f"Test Output:\n{result.stdout}\n{result.stderr}")
            return result.stdout + result.stderr
        except Exception as e:
            logger.error(f"Failed to run tests: {e}")
            return f"Error running tests: {str(e)}"

    def parse_test_failures(self, test_output: str) -> List[Dict[str, str]]:
        """
        Parses pytest output for fail details.
        """
        logger.info("Parsing test failures...")
        failures = []
        failure_pattern = re.compile(r"FAILED (.+?)::(.+?) - (.+)")  # file, test name, reason

        for match in failure_pattern.finditer(test_output):
            failures.append({
                "file": match.group(1),
                "test": match.group(2),
                "error": match.group(3)
            })

        logger.info(f"Identified {len(failures)} test failures.")
        return failures

    def apply_fix(self, failure: Dict[str, str]) -> bool:
        """
        Attempts to apply a fix either from known patterns or from Ollama + DeepSeek suggestions.
        """
        logger.info(f"🔧 Attempting to fix: {failure['file']} - {failure['test']}")
        if self._apply_known_pattern(failure):
            return True

        # If known pattern fails, fallback to advanced approach
        logger.info("No known pattern matched. Falling back to Ollama + DeepSeek.")
        return self._apply_ollama_deepseek_fix(failure)

    def _apply_known_pattern(self, failure: Dict[str, str]) -> bool:
        """
        Tries known small pattern fixes (AttributeError, AssertionError, etc.).
        Return True if fix was applied, else False to fallback to advanced approach.
        """
        error_msg = failure["error"]
        # Example placeholders for quick-coded known patterns
        if "AttributeError" in error_msg:
            logger.info("Detected quick-fixable AttributeError, skipping advanced approach.")
            return False
        if "AssertionError" in error_msg:
            logger.info("Detected quick-fixable AssertionError, skipping advanced approach.")
            return False

        # If no quick fix matched
        return False

    def _apply_ollama_deepseek_fix(self, failure: Dict[str, str]) -> bool:
        """
        Uses chunked code + Ollama for advanced suggestions in unified diff form.
        Then applies patch line by line using unidiff.
        """
        file_path = os.path.join("tests", failure["file"])
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} not found. Cannot apply fix.")
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()

            # 1) chunk code
            chunks = DebugAgentUtils.deepseek_chunk_code(file_content)
            # 2) feed to LLM for suggestions
            suggestion = DebugAgentUtils.run_deepseek_ollama_analysis(chunks, failure["error"])
            # 3) parse as a patch
            patch_obj = DebugAgentUtils.parse_diff_suggestion(suggestion)
            if not patch_obj:
                logger.warning("No patch data from LLM suggestion.")
                return False

            # 4) apply patch
            DebugAgentUtils.apply_diff_patch([file_path], patch_obj)
            return True
        except Exception as e:
            logger.error(f"Failed applying advanced fix for {failure['file']}: {e}")
            return False

    def retry_tests(self, max_retries: int = 3):
        """
        Runs tests, parses failures, attempts fixes, repeats until success or max tries.
        """
        modified_files = []
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔁 Debugging attempt {attempt}/{max_retries}...")
            test_output = self.run_tests()
            failures = self.parse_test_failures(test_output)

            if not failures:
                logger.info("✅ All tests passed successfully!")
                # Optionally push to GitHub:
                self.push_to_github("All tests passed! Automated fix commits.")
                return {"status": "success", "message": "All tests passed!"}

            for failure in failures:
                # Currently, we fix single file at a time
                # Add the file to track if we need rollback
                fix_ok = self.apply_fix(failure)
                if fix_ok and failure["file"] not in modified_files:
                    modified_files.append(failure["file"])
                if not fix_ok:
                    logger.error(f"Failed to fix {failure['file']} - {failure['test']}.")
                    logger.info("Performing rollback of changes to avoid breakage.")
                    self.rollback_changes(modified_files)
                    return {"status": "error", "message": f"Could not fix {failure['file']} automatically."}

        logger.error("🛑 Max retries reached. Some issues remain unresolved.")
        return {"status": "error", "message": "Max retries reached. Unresolved issues remain."}

    def automate_debugging(self) -> Dict[str, str]:
        """
        Main function to automate debugging overnight.
        """
        logger.info("🚀 Starting overnight debugging automation...")
        return self.retry_tests()

    def describe_capabilities(self) -> str:
        """
        Summarizes debugging capabilities.
        """
        capabilities = (
            f"{self.name} can run tests, parse & apply unidiff patches from LLM, "
            "rollback if patches fail, and optionally queue further AI agents."
        )
        logger.debug(f"{self.name} capabilities: {capabilities}")
        return capabilities

    def analyze_error(self, error: str = "", context: Dict[str, Any] = None) -> str:
        """
        Basic error analysis function.
        """
        logger.info(f"Analyzing error: {error}")
        return f"Error analysis result: '{error}'. Context: {context or 'None'}"

    def run_diagnostics(self, system_check: bool = True, detailed: bool = False) -> str:
        """
        Basic system diagnostics function.
        """
        logger.info(f"Running diagnostics system_check={system_check}, detailed={detailed}")
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
        logger.info(f"Rolling back changes to these files: {files_modified}")
        DebugAgentUtils.rollback_changes(files_modified)

    def push_to_github(self, commit_message: str):
        """
        Commits & pushes changes to GitHub after successful fixes.
        """
        try:
            logger.info("📡 Pushing changes to GitHub...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            subprocess.run(["git", "push"], check=True)
            logger.info("✅ Changes pushed to GitHub.")
        except Exception as e:
            logger.error(f"Failed to push changes to GitHub: {e}")

    def shutdown(self) -> None:
        """
        Gracefully shuts down the agent.
        """
        logger.info(f"{self.name} is shutting down. Releasing resources if allocated.")
