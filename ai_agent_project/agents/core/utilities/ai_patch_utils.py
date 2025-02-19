"""
A Python class that utilizes various AI models to generate a patch for given code and error.
This class incorporates three AI models: Ollama, DeepSeek, and OpenAI, and uses them in order of preference,
cascading down to the next when feedback is not received.

The class methods are as follows:

- `chunk_code`: This method splits a given file content into chunks for Local Language Model (LLM) processing.
- `query_llm`: This method executes a subprocess call to run a local LLM (Ollama or DeepSeek).
- `query_openai`: Queries OpenAI's GPT-4 Turbo for patch suggestions.
- `generate_patch`: Uses AI models in priority order to generate a patch suggestion.
"""

import os
import subprocess
import logging
import openai
from openai import OpenAIError  # ✅ Corrected import
from tqdm import tqdm
from typing import List, Optional

logger = logging.getLogger("AIPatchUtils")
logger.setLevel(logging.DEBUG)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo"


class AIPatchUtils:
    """
    AI-based debugging assistant for generating patch suggestions.
    Supports Ollama, DeepSeek, and OpenAI as fallback options.
    """

    @staticmethod
    def chunk_code(file_content: str, max_chars: int = 1000) -> List[str]:
        """Splits file content into manageable chunks for LLM processing."""
        return [file_content[i: i + max_chars] for i in range(0, len(file_content), max_chars)]

    @staticmethod
    def query_llm(prompt: str, model: str) -> Optional[str]:
        """
        Executes a subprocess call to run a local LLM (Ollama or DeepSeek).
        Handles errors and provides logs for debugging.
        """
        try:
            result = subprocess.run(["ollama", "run", model, prompt], capture_output=True, text=True)

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            else:
                logger.warning(f"⚠️ LLM ({model}) failed: {result.stderr.strip()}")
        except FileNotFoundError:
            logger.warning(f"🚨 Model {model} not found. Skipping...")
        except subprocess.SubprocessError as e:
            logger.error(f"⚠️ Error executing subprocess for {model}: {str(e)}")

        return None

    @staticmethod
    def query_openai(prompt: str) -> Optional[str]:
        """
        Queries OpenAI GPT for patch suggestions with proper error handling.
        """
        if not OPENAI_API_KEY:
            logger.error("🚨 OpenAI API Key not set. Skipping OpenAI fallback.")
            return None

        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024
            )
            return response["choices"][0]["message"]["content"].strip()

        except AttributeError as e:
            logger.error(f"🚨 OpenAI module error: {e}")
        except OpenAIError as e:
            logger.error(f"⚠️ OpenAI API call failed: {e}")
        except Exception as e:
            logger.error(f"⚠️ Unexpected OpenAI error: {e}")

        return None

    @classmethod
    def generate_patch(cls, file_content: str, error_msg: str) -> str:
        """
        Uses AI models to generate a patch for the given error and code.
        Prioritizes Ollama → DeepSeek → OpenAI in that order.
        """
        chunks = cls.chunk_code(file_content)
        prompt = f"""
        Analyze the following code and error:
        Code:
        {' '.join(chunks)}

        Error:
        {error_msg}

        Suggest a minimal fix in unified diff format (`diff --git`...).
        """

        suggestions = []

        # Try Ollama (Mistral Model)
        with tqdm(total=len(chunks), desc="Processing with Ollama", unit="chunk") as pbar:
            for chunk in chunks:
                patch = cls.query_llm(prompt, "mistral")
                if patch and "diff --git" in patch:
                    suggestions.append(patch)
                pbar.update(1)

        # If no results, fallback to DeepSeek
        if not suggestions:
            logger.warning("⚠️ Ollama failed. Trying DeepSeek.")
            with tqdm(total=len(chunks), desc="Processing with DeepSeek", unit="chunk") as pbar:
                for chunk in chunks:
                    patch = cls.query_llm(prompt, "deepseek-coder")
                    if patch and "diff --git" in patch:
                        suggestions.append(patch)
                    pbar.update(1)

        # If no results, fallback to OpenAI
        if not suggestions:
            logger.warning("⚠️ Both Ollama and DeepSeek failed. Trying OpenAI.")
            patch = cls.query_openai(prompt)
            if patch and "diff --git" in patch:
                suggestions.append(patch)

        combined_patch = "\n".join(suggestions).strip()

        if combined_patch:
            logger.info("✅ Successfully generated AI patch.")
        else:
            logger.warning("❌ No valid patch data generated.")

        return combined_patch
