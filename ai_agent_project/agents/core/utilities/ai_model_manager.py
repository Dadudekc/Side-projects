"""
This module defines the AIModelManager class, which manages different AI models for generating
patch suggestions for code errors.

This class supports various types of AI models (both local and cloud-based) and prioritizes them
based on performance. It provides functions to generate patch suggestions based on the error message,
code context, and test file. It also tracks past AI performance, retries failed models if necessary,
and assigns confidence scores to the generated patches.
"""

import os
import subprocess
import logging
import openai
from typing import Optional
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager
from ai_engine.confidence_manager import AIConfidenceManager

logger = logging.getLogger("AIModelManager")
logger.setLevel(logging.DEBUG)

class AIModelManager:
    """
    A unified AI debugging system that selects the best available model to generate patch suggestions.

    Supports:
      - Local models (e.g. Mistral, DeepSeek) via Ollama
      - Cloud models (OpenAI GPT-4 fallback)

    Features:
      - AI Confidence Tracking: Assigns and updates confidence scores for generated patches.
      - AI Patch History: Tracks previous patch attempts to avoid repeating failures.
      - Auto-Retries: Retries generating patches if the confidence improves.
    
    Attributes:
      openai_api_key (str): The API key for OpenAI, loaded from environment.
      patch_tracker (PatchTrackingManager): Manages patch history.
      confidence_manager (AIConfidenceManager): Tracks and assigns confidence scores.
      model_priority (list): Ordered list of models to try.
    """

    # Expose subprocess and openai at the class level (for testing convenience)
    subprocess = subprocess
    openai = openai

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")  # Load OpenAI key from environment
        self.patch_tracker = PatchTrackingManager()
        self.confidence_manager = AIConfidenceManager()

        # Model priority order (modify as needed)
        self.model_priority = ["mistral", "deepseek", "openai"]

    def generate_patch(self, error_msg: str, code_context: str, test_file: str) -> Optional[str]:
        """
        Generates a patch suggestion using the best available AI model.

        Fallback order: Mistral → DeepSeek → OpenAI.
        If a patch is generated, its confidence is evaluated and, if improved, the patch is accepted.

        Args:
            error_msg (str): The error message encountered.
            code_context (str): The code context surrounding the error.
            test_file (str): The test file where the error was encountered.

        Returns:
            Optional[str]: A unified diff patch string if successful, or None otherwise.
        """
        request_prompt = self._format_prompt(error_msg, code_context, test_file)
        error_signature = self._compute_error_signature(error_msg, code_context)

        # Track AI confidence for previous attempts
        past_confidence = self.confidence_manager.calculate_confidence(error_signature)

        for model in self.model_priority:
            patch = self._generate_with_model(model, request_prompt)
            if patch:
                confidence_score, reason = self.confidence_manager.assign_confidence_score(error_signature, patch)

                if confidence_score > past_confidence:
                    logger.info(f"✅ AI confidence improved ({past_confidence} ➡ {confidence_score}). Patch accepted.")

                    # Store high-confidence patches for reuse
                    if confidence_score >= 0.75:
                        self.confidence_manager.store_patch(error_signature, patch, confidence_score)

                    return patch
                else:
                    logger.warning(f"⚠️ AI confidence remains low ({confidence_score}). Skipping patch for model {model}.")
                    
        logger.error("❌ All AI models failed to generate a useful patch.")
        return None

    def _format_prompt(self, error_msg: str, code_context: str, test_file: str) -> str:
        """
        Formats the debugging request into a structured AI prompt.

        Args:
            error_msg (str): The error message.
            code_context (str): The code context.
            test_file (str): The test file in which the error occurred.

        Returns:
            str: A formatted prompt string.
        """
        return (
            f"You are an expert debugging assistant.\n\n"
            f"Test File: {test_file}\n"
            f"Error Message: {error_msg}\n"
            f"Code Context:\n{code_context}\n\n"
            "Generate a fix for the code in unified diff format (`diff --git` style)."
        )

    def _generate_with_model(self, model: str, prompt: str) -> Optional[str]:
        """
        Dynamically calls the appropriate AI model based on the given model name.

        Args:
            model (str): The model name (e.g., "mistral", "deepseek", "openai").
            prompt (str): The formatted prompt.

        Returns:
            Optional[str]: The patch suggestion generated by the AI model.
        """
        if model == "openai":
            return self._generate_with_openai(prompt)
        else:
            return self._generate_with_ollama(model, prompt)

    def _generate_with_ollama(self, model: str, prompt: str) -> Optional[str]:
        """
        Calls a local Ollama model (e.g. Mistral or DeepSeek) to generate a patch suggestion.

        Args:
            model (str): The local model name.
            prompt (str): The prompt to send.

        Returns:
            Optional[str]: The generated patch if successful, or None otherwise.
        """
        try:
            cmd = ["ollama", "run", model, prompt]
            result = self.subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning(f"⚠️ {model.capitalize()} failed: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ {model.capitalize()} call failed: {e}")
        return None

    def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """
        Calls OpenAI GPT-4 to generate a patch suggestion.

        Args:
            prompt (str): The prompt to send to the OpenAI API.

        Returns:
            Optional[str]: The generated patch if successful, or None otherwise.
        """
        if not self.openai_api_key:
            logger.error("❌ OpenAI API key not set. Skipping GPT-4 fallback.")
            return None

        try:
            response = self.openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512
            )
            return response["choices"][0]["message"]["content"].strip()
        except openai.error.OpenAIError as e:
            logger.error("❌ OpenAI GPT-4 call failed: %s", e)
        except Exception as e:
            logger.error("❌ Unexpected error with OpenAI GPT-4: %s", e)
        return None

    def _compute_error_signature(self, error_msg: str, code_context: str) -> str:
        """
        Computes a unique error signature based on the error message and code context.

        Args:
            error_msg (str): The error message.
            code_context (str): The code context.

        Returns:
            str: A SHA-256 hash representing the error signature.
        """
        import hashlib
        h = hashlib.sha256()
        h.update(error_msg.encode("utf-8"))
        h.update(code_context.encode("utf-8"))
        return h.hexdigest()
