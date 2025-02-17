import logging
import os
import re
import shutil
from typing import Dict, Optional
from ai_engine.models.debugger.learning_db import LearningDB
from agents.core.utilities.debug_agent_utils import DebugAgentUtils

logger = logging.getLogger(__name__)

class AutoFixer:
    """
    Applies quick fixes for known error patterns and advanced LLM-based patches.
    """

    def __init__(self):
        self.learning_db = LearningDB()

    def apply_fix(self, failure: Dict[str, str]) -> bool:
        """
        Attempts to fix the provided test failure.
        """
        logger.info(f"🔧 Fixing: {failure['file']} - {failure['test']}")

        if self._apply_known_pattern(failure):
            logger.info(f"✅ Quick fix applied successfully for {failure['file']}")
            return True
        
        learned_fix = self.learning_db.search_learned_fix(failure["error"])
        if learned_fix:
            logger.info(f"✅ Applying learned fix for {failure['file']}")
            return self._apply_learned_fix(failure, learned_fix)

        logger.info(f"🔍 Attempting LLM-based fix for {failure['file']}")
        return self._apply_llm_fix(failure)

    def _apply_llm_fix(self, failure: Dict[str, str]) -> bool:
        """
        Uses DebugAgentUtils to generate and apply an LLM-based patch.
        """
        file_path = os.path.join("tests", failure["file"])
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return False

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        chunks = DebugAgentUtils.deepseek_chunk_code(file_content)
        logger.info(f"🔍 Generated {len(chunks)} chunks for LLM analysis.")

        suggestion = DebugAgentUtils.run_deepseek_ollama_analysis(chunks, failure["error"])
        if not suggestion.strip():
            logger.error("❌ LLM returned an empty patch suggestion.")
            return False

        patch = DebugAgentUtils.parse_diff_suggestion(suggestion)
        if not patch or len(patch) == 0:
            logger.error("❌ Parsed patch is empty. Cannot apply fix.")
            return False

        # Create a backup before modifying the file
        backup_path = file_path + ".backup"
        try:
            shutil.copy(file_path, backup_path)
            logger.info(f"✅ Created backup at {backup_path}")
        except Exception as e:
            logger.error(f"❌ Failed to create backup: {e}")
            return False

        try:
            DebugAgentUtils.apply_diff_patch([file_path], patch)
            logger.info("✅ LLM-based patch applied successfully.")
            self.learning_db.store_fix(failure["error"], suggestion)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to apply LLM patch: {e}")
            shutil.copy(backup_path, file_path)
            logger.info("🔄 Restored original file from backup.")
            return False

    def _apply_known_pattern(self, failure: Dict[str, str]) -> bool:
        """
        Applies quick fixes based on known error patterns.
        """
        error_msg = failure["error"]
        file_name = failure["file"]

        if "AttributeError" in error_msg:
            return self._quick_fix_missing_attribute(file_name, error_msg)
        if "AssertionError" in error_msg:
            return self._quick_fix_assertion_mismatch(file_name, error_msg)
        if "ImportError" in error_msg:
            return self._quick_fix_import_error(file_name, error_msg)
        if "TypeError" in error_msg and "missing" in error_msg:
            return self._quick_fix_type_error(file_name, error_msg)
        if "IndentationError" in error_msg:
            return self._quick_fix_indentation(file_name)

        return False

    def _apply_learned_fix(self, failure: Dict[str, str], fix: str) -> bool:
        """
        Applies a fix retrieved from the learning database.
        """
        file_path = os.path.join("tests", failure["file"])
        if not os.path.exists(file_path):
            return False
        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n" + fix + "\n")
        logger.info(f"✅ Applied learned fix to {file_path}")
        return True

    def _quick_fix_type_error(self, file_name: str, error_msg: str) -> bool:
        """
        Attempts to fix a TypeError caused by missing arguments.
        """
        match = re.search(r"(.+?)\(\) missing (\d+) required positional argument", error_msg)
        if not match:
            return False
        function_name, missing_count_str = match.groups()
        try:
            missing_count = int(missing_count_str)
        except ValueError:
            return False

        file_path = os.path.join("tests", file_name)
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            changed = False
            for i, line in enumerate(lines):
                if re.search(rf"{function_name}\((.*?)\)", line):
                    placeholders = ", ".join(["None"] * missing_count)
                    lines[i] = re.sub(rf"{function_name}\((.*?)\)", f"{function_name}(\\1, {placeholders})", line)
                    changed = True
                    break

            if changed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                logger.info(f"✅ TypeError fix applied to {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Could not fix TypeError: {e}")
            return False

    def _quick_fix_indentation(self, file_name: str) -> bool:
        """
        Converts tabs to spaces to fix indentation errors.
        """
        file_path = os.path.join("tests", file_name)
        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            converted = [line.replace("\t", "    ") for line in lines]

            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(converted)

            logger.info(f"✅ Fixed indentation in {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Could not fix indentation: {e}")
            return False
