from typing import Dict, Any, List
from typing import Dict, List
import logging
import subprocess
import re
import os
from typing import List
from unidiff import PatchSet
from tqdm import tqdm
import openai  # OpenAI API for backup
import typing 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# OpenAI Fallback Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Ensure the key is set in env variables
OPENAI_MODEL = "gpt-4-turbo"  # Change as needed

class DebugAgentUtils:
    """
    A collection of advanced debugging and AI-driven fix utilities, including:
     - Patch/diff (using unidiff)
     - Partial file merges
     - Code chunking for DeepSeek
     - Agent queuing
     - Rollback systems (via Git)
    """

    @staticmethod
    def deepseek_chunk_code(file_content: str, max_chars: int = 1000) -> List[str]:
        """
        Splits file content into smaller chunks to feed into an LLM or 
        DeepSeek for advanced contextual analysis.
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
        model: str = "mistral"  # Default primary model for Ollama
    ) -> str:
        """
        Feeds each chunk + error message into Ollama (or any local LLM) to gather patch suggestions.
        If Ollama fails, it retries with DeepSeek. If both fail, it falls back to OpenAI's GPT API.
        """
        suggestions = []
        fallback_to_openai = False  # Tracks if we should use OpenAI as a backup

        with tqdm(total=len(chunks), desc="Processing Chunks with Ollama", unit="chunk") as pbar:
            for i, chunk in enumerate(chunks):
                prompt = (
                    f"Chunk {i+1}:\n{chunk}\n\n"
                    f"Error encountered: {error_msg}\n"
                    "Suggest minimal changes in a unified diff format (`diff --git`...)."
                )

                # Attempt Ollama First (Mistral)
                try:
                    cmd = ["ollama", "run", model, prompt]
                    logger.info(f"🟢 Sending chunk {i+1}/{len(chunks)} to Ollama ({model})...")
                    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
                    if result.returncode == 0 and result.stdout.strip():
                        suggestions.append(result.stdout.strip())
                        logger.info(f"✅ Ollama successfully processed chunk {i+1}.")
                    else:
                        logger.warning(f"⚠️ Ollama failed on chunk {i+1}: {result.stderr}")
                        fallback_to_openai = True
                except FileNotFoundError:
                    logger.critical("🚨 Ollama is not installed or not in PATH. Skipping to next model.")
                    fallback_to_openai = True
                except Exception as e:
                    logger.error(f"❌ Could not call Ollama for chunk {i+1}: {e}")
                    fallback_to_openai = True

                pbar.update(1)

        # Fallback 1: DeepSeek (if Ollama fails)
        if fallback_to_openai and not suggestions:
            logger.warning("⚠️ Ollama failed. Attempting fallback with DeepSeek LLM.")
            with tqdm(total=len(chunks), desc="Processing with DeepSeek", unit="chunk") as pbar:
                for i, chunk in enumerate(chunks):
                    try:
                        deepseek_cmd = ["deepseek", "run", "deepseek-coder", prompt]
                        result = subprocess.run(deepseek_cmd, capture_output=True, text=True, encoding="utf-8")
                        if result.returncode == 0 and result.stdout.strip():
                            suggestions.append(result.stdout.strip())
                            logger.info(f"✅ DeepSeek successfully processed chunk {i+1}.")
                        else:
                            logger.warning(f"⚠️ DeepSeek failed on chunk {i+1}: {result.stderr}")
                            fallback_to_openai = True
                    except FileNotFoundError:
                        logger.critical("🚨 DeepSeek is not installed. Skipping to OpenAI fallback.")
                        fallback_to_openai = True
                    except Exception as e:
                        logger.error(f"❌ DeepSeek failed on chunk {i+1}: {e}")
                        fallback_to_openai = True
                    pbar.update(1)

        # Fallback 2: OpenAI GPT (if both fail)
        if fallback_to_openai and not suggestions:
            logger.warning("⚠️ Both Ollama and DeepSeek failed. Falling back to OpenAI GPT.")
            try:
                openai_prompt = (
                    "You are a code repair assistant. Analyze the following error message "
                    "and suggest a minimal fix in a unified diff format (`diff --git`).\n\n"
                    f"Error: {error_msg}\n\n"
                    f"Code:\n{'\n'.join(chunks)}"
                )
                response = openai.ChatCompletion.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": openai_prompt}],
                    max_tokens=1024
                )
                openai_suggestion = response["choices"][0]["message"]["content"].strip()
                if openai_suggestion:
                    logger.info("✅ OpenAI GPT successfully provided a patch.")
                    suggestions.append(openai_suggestion)
                else:
                    logger.warning("⚠️ OpenAI returned an empty response.")
            except openai.error.OpenAIError as e:
                logger.error(f"❌ OpenAI API call failed: {e}")

        combined_suggestion = "\n".join(suggestions).strip()
        if combined_suggestion:
            logger.info("🛠️ Successfully merged suggestions into a single patch.")
        else:
            logger.warning("⚠️ No valid patch data generated. All LLM attempts failed.")

        return combined_suggestion

    @staticmethod
    def parse_diff_suggestion(suggestion: str) -> PatchSet:
        """
        Parses a unified diff from the LLM into a PatchSet for line-by-line application.
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
        """
        path_set = {os.path.abspath(p) for p in file_paths}
        for patched_file in patch:
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
        """
        with open(file_path, "r", encoding="utf-8") as f:
            original_lines = f.readlines()
        new_lines = original_lines[:]
        offset = 0
        for hunk in patched_file:
            for hunk_line in hunk:
                line_number = hunk_line.source_line_no - 1 + offset
                if hunk_line.is_removed:
                    if 0 <= line_number < len(new_lines):
                        new_lines.pop(line_number)
                        offset -= 1
                elif hunk_line.is_added:
                    if line_number < 0:
                        line_number = 0
                    if line_number > len(new_lines):
                        line_number = len(new_lines)
                    new_lines.insert(line_number, hunk_line.value)
                    offset += 1
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
        Schedules or orchestrates multiple specialized agents for deeper refactor or doc generation.
        """
        logger.info(f"🔀 Queuing additional agents: {agent_list}")
        return {"status": "queued", "agents": agent_list}
