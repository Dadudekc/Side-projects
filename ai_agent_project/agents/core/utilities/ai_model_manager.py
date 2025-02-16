import os
import subprocess
import logging
import openai
from typing import Optional, List, Dict, Tuple
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager
from ai_engine.confidence_manager import AIConfidenceManager

logger = logging.getLogger("AIModelManager")
logger.setLevel(logging.DEBUG)


class AIModelManager:
    """
    A unified AI debugging system that selects the best available model.
    
    Supports:
      - Local models (Mistral, DeepSeek)
      - Cloud models (OpenAI GPT-4 fallback)
    
    Features:
      ✅ AI Confidence Tracking (Assigns confidence to patches)
      ✅ AI Patch History (Avoids repeating bad patches)
      ✅ Auto-Retries if AI improves confidence
    """

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
        If a patch fails, AI **retries with modifications** if confidence improves.
        """
        request_prompt = self._format_prompt(error_msg, code_context, test_file)
        error_signature = self._compute_error_signature(error_msg, code_context)

        # Track AI confidence for previous attempts
        past_confidence = self.confidence_manager.get_confidence(error_signature)

        for model in self.model_priority:
            patch = self._generate_with_model(model, request_prompt)
            if patch:
                confidence_score, reason = self.confidence_manager.assign_confidence_score(error_signature, patch)

                # Check if AI confidence has improved
                if confidence_score > past_confidence:
                    logger.info(f"✅ AI confidence improved ({past_confidence} ➡ {confidence_score}). Patch accepted.")
                    return patch

                logger.warning(f"⚠️ AI confidence remains low ({confidence_score}). Skipping patch.")

        logger.error("❌ All AI models failed to generate a useful patch.")
        return None

    def _format_prompt(self, error_msg: str, code_context: str, test_file: str) -> str:
        """Formats the debugging request into a structured AI prompt."""
        return (
            f"You are an expert debugging assistant.\n\n"
            f"Test File: {test_file}\n"
            f"Error Message: {error_msg}\n"
            f"Code Context:\n{code_context}\n\n"
            f"Generate a fix for the code in unified diff format (`diff --git` style)."
        )

    def _generate_with_model(self, model: str, prompt: str) -> Optional[str]:
        """Dynamically calls the appropriate AI model."""
        if model == "openai":
            return self._generate_with_openai(prompt)
        else:
            return self._generate_with_ollama(model, prompt)

    def _generate_with_ollama(self, model: str, prompt: str) -> Optional[str]:
        """Calls a local Ollama model (Mistral/DeepSeek)."""
        try:
            cmd = ["ollama", "run", model, prompt]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning(f"⚠️ {model.capitalize()} failed: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ {model.capitalize()} call failed: {e}")
        return None

    def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """Calls OpenAI GPT-4 if local models fail."""
        if not self.openai_api_key:
            logger.error("❌ OpenAI API key not set. Skipping GPT-4 fallback.")
            return None

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error("❌ OpenAI GPT-4 call failed: %s", e)
        return None

    def _compute_error_signature(self, error_msg: str, code_context: str) -> str:
        """
        Computes a unique error signature based on the error message and code context.
        This helps track AI patch success rates.
        """
        import hashlib
        h = hashlib.sha256()
        h.update(error_msg.encode("utf-8"))
        h.update(code_context.encode("utf-8"))
        return h.hexdigest()
