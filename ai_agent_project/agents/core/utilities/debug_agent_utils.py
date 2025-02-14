import logging
import subprocess
import re
import os
from typing import Any, Dict, List, Optional
from unidiff import PatchSet, Hunk

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DebugAgentUtils:
    """
    A collection of advanced debugging and AI-driven fix utilities, including:
     - Patch/diff (using unidiff),
     - Partial file merges,
     - Code chunking for DeepSeek,
     - Agent queuing,
     - Rollback systems (via Git).
    """

    @staticmethod
    def deepseek_chunk_code(file_content: str, max_chars: int = 1000) -> List[str]:
        """
        Splits file content into smaller chunks to feed into an LLM or 
        DeepSeek for advanced contextual analysis.

        Args:
            file_content (str): The entire code file as a string.
            max_chars (int): Maximum chunk size for each context.

        Returns:
            List[str]: Code chunks that can be processed by the LLM.
        """
        chunks = []
        start = 0
        while start < len(file_content):
            end = min(len(file_content), start + max_chars)
            chunks.append(file_content[start:end])
            start = end
        return chunks

    @staticmethod
    def run_deepseek_ollama_analysis(
        chunks: List[str],
        error_msg: str,
        model: str = "llama2-base"
    ) -> str:
        """
        Feeds each chunk + error message into Ollama (or any local LLM) 
        to gather partial suggestions. Merges them into a final patch suggestion.

        Args:
            chunks (List[str]): The code chunks from deepseek_chunk_code.
            error_msg (str): The error encountered, used for context.
            model (str): The Ollama model name.

        Returns:
            str: The combined patch suggestion from the LLM (unified diff).
        """
        suggestions = []
        for i, chunk in enumerate(chunks):
            prompt = (
                f"Chunk {i+1}:\n{chunk}\n\n"
                f"Error encountered: {error_msg}\n"
                "Suggest minimal changes in a unified diff format (`diff --git`...)."
            )
            try:
                cmd = ["ollama", "prompt", prompt, "--model", model, "--max-tokens", "512"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    suggestions.append(result.stdout.strip())
                else:
                    logger.error(f"❌ Ollama call failed on chunk {i+1}: {result.stderr}")
            except Exception as e:
                logger.error(f"❌ Could not call Ollama for chunk {i+1}: {e}")

        # Merge partial suggestions into a single potential patch
        combined_suggestion = "\n".join(suggestions)
        logger.info("Merged suggestion from all code chunks into one patch.")
        return combined_suggestion

    @staticmethod
    def parse_diff_suggestion(suggestion: str) -> PatchSet:
        """
        Parses a unified diff from the LLM into a PatchSet for line-by-line application.

        Args:
            suggestion (str): The patch/diff text from the LLM.

        Returns:
            PatchSet: A unidiff PatchSet object that can be applied line-by-line.
        """
        try:
            patch = PatchSet(suggestion)
            return patch
        except Exception as e:
            logger.error(f"❌ Could not parse diff suggestion as PatchSet: {e}")
            return PatchSet()  # empty patchset

    @staticmethod
    def apply_diff_patch(file_paths: List[str], patch: PatchSet) -> None:
        """
        Applies a unidiff patch line-by-line to the specified files.

        Args:
            file_paths (List[str]): The file paths that might be patched.
            patch (PatchSet): The parsed PatchSet containing all diffs.

        Raises:
            ValueError: If a patched file does not exist or lines mismatch.
        """
        # Convert list to set for quick membership checks
        path_set = {os.path.abspath(p) for p in file_paths}

        for patched_file in patch:
            # Typically, patched_file.path is the new name
            target_path = patched_file.path
            abs_target_path = os.path.abspath(target_path)

            if abs_target_path not in path_set:
                logger.warning(f"File in patch '{patched_file.path}' is not in {file_paths}. Skipping.")
                continue

            logger.info(f"🩹 Applying patch to {patched_file.path} ...")
            DebugAgentUtils._apply_file_patch(abs_target_path, patched_file)

    @staticmethod
    def _apply_file_patch(file_path: str, patched_file) -> None:
        """
        Helper that applies a single file patch using unidiff.

        Args:
            file_path (str): Path to the file to patch.
            patched_file: unidiff object that contains hunks to apply.
        """
        # Load original content
        with open(file_path, "r", encoding="utf-8") as f:
            original_lines = f.readlines()

        # Convert lines to list of strings (stripping newlines not always needed)
        new_lines = original_lines[:]

        # We apply each hunk in the patch
        offset = 0
        for hunk in patched_file:
            for hunk_line in hunk:
                # unidiff HunkLine, check if it's addition, removal, context, etc.
                line_number = hunk_line.source_line_no - 1 + offset
                if hunk_line.is_removed:
                    # remove line
                    if 0 <= line_number < len(new_lines):
                        new_lines.pop(line_number)
                        offset -= 1
                elif hunk_line.is_added:
                    # add line
                    # insertion at line_number
                    if line_number < 0:
                        line_number = 0
                    if line_number > len(new_lines):
                        line_number = len(new_lines)
                    new_lines.insert(line_number, hunk_line.value)
                    offset += 1
                # if context line, do nothing

        # write updated lines
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

        logger.info(f"✅ Patch applied to {file_path} successfully.")

    @staticmethod
    def rollback_changes(files_modified: List[str]):
        """
        Rolls back changes made to the specified files (via Git).
        """
        logger.info("⚠️ Rolling back changes to avoid permanent breakage.")
        for file in files_modified:
            try:
                subprocess.run(["git", "restore", file], check=True)
                logger.info(f"Reverted changes in {file}.")
            except Exception as e:
                logger.error(f"❌ Failed to rollback {file}: {e}")

        logger.info("✅ Rollback completed. Manual review recommended if issues persist.")

    @staticmethod
    def queue_additional_agents(agent_list: List[str]) -> Dict[str, Any]:
        """
        Schedules or orchestrates multiple specialized agents 
        for deeper refactor or doc generation.
        """
        # Example: Call codeRefactorAgent, docAgent, etc.
        # or pass them to a pipeline orchestrator.
        logger.info(f"🔀 Queuing additional agents: {agent_list}")
        # Real logic might do something like:
        # for agent in agent_list:
        #    runAgent(agent)
        return {"status": "queued", "agents": agent_list}
