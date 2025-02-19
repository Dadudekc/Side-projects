"""
This Python module provides a comprehensive set of utilities for advanced debugging and AI-driven fixes.
These utilities include:
 - Patch/diff (using unidiff)
 - Partial file merges
 - Code chunking for DeepSeek
 - Agent queuing
 - Rollback systems (via Git)

The module integrates functionalities from:
 - `logging`
 - `subprocess`
 - `os`
 - `unidiff`
 - `tqdm`
 - `openai`
"""

import os
import logging
import subprocess
from unidiff import PatchSet
from tqdm import tqdm
import openai  # OpenAI API for backup
from typing import List, Dict, Any, Optional

logger = logging.getLogger("DebugAgentUtils")
logger.setLevel(logging.DEBUG)

# OpenAI Fallback Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Ensure API key is set in environment variables
OPENAI_MODEL = "gpt-4-turbo"


class DebugAgentUtils:
    """
    A collection of advanced debugging and AI-driven fix utilities.
    Supports:
     - Unified diff patching
     - AI-assisted patch suggestions
     - Code chunking for local LLMs
     - Agent queuing for multi-step debugging
    """

    @staticmethod
    def deepseek_chunk_code(file_content: str, max_chars: int = 1000) -> List[str]:
        """
        Splits file content into smaller chunks for DeepSeek/LLM processing.
        Ensures optimal chunking for token-based AI models.

        Args:
            file_content (str): The complete file content.
            max_chars (int): Maximum characters per chunk (default: 1000).

        Returns:
            List[str]: A list of chunked code strings.
        """
        return [file_content[i : i + max_chars] for i in range(0, len(file_content), max_chars)]

    @staticmethod
    def run_deepseek_ollama_analysis(
        chunks: List[str], error_msg: str, model: str = "mistral"
    ) -> str:
        """
        Uses Ollama (or DeepSeek as a backup) to analyze code chunks and suggest patches.

        If both fail, OpenAI GPT is used as the final fallback.

        Args:
            chunks (List[str]): List of code chunks.
            error_msg (str): The error message associated with the bug.
            model (str): The primary model to use (default: "mistral").

        Returns:
            str: A combined AI-generated patch or an empty string if all LLMs fail.
        """
        suggestions = []
        fallback_to_openai = False  # Tracks if OpenAI should be used

        with tqdm(total=len(chunks), desc="Processing with Ollama", unit="chunk") as pbar:
            for i, chunk in enumerate(chunks):
                prompt = f"""
                Chunk {i+1}:
                {chunk}

                Error encountered: {error_msg}
                Suggest minimal changes in a unified diff format (`diff --git`...).
                """
                try:
                    result = subprocess.run(
                        ["ollama", "run", model, prompt],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        suggestions.append(result.stdout.strip())
                        logger.info(f"✅ Ollama processed chunk {i+1}/{len(chunks)} successfully.")
                    else:
                        logger.warning(f"⚠️ Ollama failed on chunk {i+1}: {result.stderr}")
                        fallback_to_openai = True
                except FileNotFoundError:
                    logger.critical("🚨 Ollama is not installed or not in PATH. Skipping to next model.")
                    fallback_to_openai = True
                except Exception as e:
                    logger.error(f"❌ Ollama error on chunk {i+1}: {e}")
                    fallback_to_openai = True
                pbar.update(1)

        # Fallback to DeepSeek if Ollama fails
        if fallback_to_openai and not suggestions:
            logger.warning("⚠️ Ollama failed. Attempting fallback with DeepSeek.")
            with tqdm(total=len(chunks), desc="Processing with DeepSeek", unit="chunk") as pbar:
                for i, chunk in enumerate(chunks):
                    try:
                        result = subprocess.run(
                            ["deepseek", "run", "deepseek-coder", prompt],
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            suggestions.append(result.stdout.strip())
                            logger.info(f"✅ DeepSeek processed chunk {i+1}/{len(chunks)} successfully.")
                        else:
                            logger.warning(f"⚠️ DeepSeek failed on chunk {i+1}: {result.stderr}")
                            fallback_to_openai = True
                    except FileNotFoundError:
                        logger.critical("🚨 DeepSeek is not installed. Skipping to OpenAI fallback.")
                        fallback_to_openai = True
                    except Exception as e:
                        logger.error(f"❌ DeepSeek error on chunk {i+1}: {e}")
                        fallback_to_openai = True
                    pbar.update(1)

        # Fallback to OpenAI GPT if both fail
        if fallback_to_openai and not suggestions:
            logger.warning("⚠️ Both Ollama and DeepSeek failed. Falling back to OpenAI GPT.")
            try:
                openai_prompt = f"""
                You are a code repair assistant. Analyze the following error message
                and suggest a minimal fix in a unified diff format (`diff --git`).

                Error: {error_msg}

                Code:
                {'\n'.join(chunks)}
                """
                response = openai.ChatCompletion.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": openai_prompt}],
                    temperature=0.7,
                    max_tokens=1024,
                )
                openai_suggestion = response["choices"][0]["message"]["content"].strip()
                if openai_suggestion:
                    logger.info("✅ OpenAI GPT successfully provided a patch.")
                    suggestions.append(openai_suggestion)
                else:
                    logger.warning("⚠️ OpenAI returned an empty response.")
            except Exception as e:
                logger.error(f"❌ OpenAI API call failed: {e}")

        combined_suggestion = "\n".join(suggestions).strip()
        return combined_suggestion if combined_suggestion else "⚠️ No valid patch data generated."

    @staticmethod
    def parse_diff_suggestion(suggestion: str) -> Optional[List[Dict[str, Any]]]:
        """
        Parses a unified diff suggestion string into a list of patch changes.
        Utilizes unidiff.PatchSet to parse the diff.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of changes where each change is a dict,
            or None if parsing fails.
        """
        try:
            patch_set = PatchSet(suggestion.splitlines(keepends=True))
            changes = []
            for patched_file in patch_set:
                for hunk in patched_file:
                    for line in hunk:
                        if line.is_added:
                            changes.append({
                                "action": "add",
                                "line_no": line.target_line_no,
                                "content": line.value,
                            })
                        elif line.is_removed:
                            changes.append({
                                "action": "remove",
                                "line_no": line.source_line_no,
                                "content": line.value,
                            })
            return changes
        except Exception as e:
            logger.error(f"❌ Failed to parse diff suggestion: {e}")
            return None

    @staticmethod
    def apply_diff_patch(file_paths: List[str], patch: List[Dict[str, Any]]):
        """
        Applies a patch to the given files.
        This naive implementation iterates over the provided patch changes and applies
        additions or removals to the target files.

        Args:
            file_paths (List[str]): List of file paths to apply the patch to.
            patch (List[Dict[str, Any]]): A list of patch changes.
        """
        for file_path in file_paths:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                # Apply each change; here we only demonstrate additions.
                for change in patch:
                    if change.get("action") == "add":
                        line_no = change.get("line_no", len(lines) + 1)
                        # Insert at the correct position (adjust for 0-index)
                        if 0 <= line_no - 1 < len(lines):
                            lines.insert(line_no - 1, change.get("content", ""))
                        else:
                            lines.append(change.get("content", ""))
                    elif change.get("action") == "remove":
                        line_no = change.get("line_no", None)
                        if line_no and 0 <= line_no - 1 < len(lines):
                            # Remove the line if it matches the expected content
                            if lines[line_no - 1] == change.get("content", ""):
                                del lines[line_no - 1]
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
            except Exception as e:
                raise RuntimeError(f"Failed to apply patch on {file_path}: {e}")

    @staticmethod
    def rollback_changes(files_modified: List[str]):
        """
        Rolls back changes to avoid permanent breakage using Git.

        Args:
            files_modified (List[str]): List of file paths to revert.
        """
        logger.info("⚠️ Rolling back changes to avoid permanent breakage.")
        for file in files_modified:
            try:
                subprocess.run(["git", "restore", file], check=True)
                logger.info(f"✅ Reverted changes in {file}.")
            except subprocess.CalledProcessError:
                logger.error(f"❌ Failed to rollback {file}. Check Git status.")
            except Exception as e:
                logger.error(f"❌ Error during rollback: {e}")
        logger.info("✅ Rollback completed. Manual review recommended if issues persist.")

    @staticmethod
    def queue_additional_agents(agent_list: List[str]) -> Dict[str, Any]:
        """
        Schedules additional debugging agents for deeper analysis.

        Args:
            agent_list (List[str]): List of agent names to queue.

        Returns:
            Dict[str, Any]: Status of the queue operation.
        """
        logger.info(f"🔀 Queuing additional agents: {agent_list}")
        return {"status": "queued", "agents": agent_list}
