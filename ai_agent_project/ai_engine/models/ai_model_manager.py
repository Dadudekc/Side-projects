import os
import json
import hashlib
import subprocess
import logging
import openai
from typing import Optional, Dict
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
      ✅ Save and Load Model Data
    """

    MODEL_STORAGE_DIR = "models"  # Directory for storing model metadata

    def __init__(self):
        """Initialize AIModelManager with confidence tracking and patch history."""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")  # Load OpenAI key from environment
        self.patch_tracker = PatchTrackingManager()
        self.confidence_manager = AIConfidenceManager()
        self.model = {}  # Placeholder for model data

        # Model priority order (modify as needed)
        self.model_priority = ["mistral", "deepseek", "openai"]

        # Ensure model storage directory exists
        os.makedirs(self.MODEL_STORAGE_DIR, exist_ok=True)

    def generate_patch(self, error_msg: str, code_context: str, test_file: str) -> Optional[str]:
        """
        Generates a patch suggestion using the best available AI model.

        Fallback order: Mistral → DeepSeek → OpenAI.
        If a patch fails, AI **retries with modifications** if confidence improves.
        """
        request_prompt = self._format_prompt(error_msg, code_context, test_file)
        error_signature = self._compute_error_signature(error_msg, code_context)

        # Track AI confidence for previous attempts
        past_confidence = self.confidence_manager.get_best_high_confidence_patch(error_signature) or 0

        for model in self.model_priority:
            patch = self._generate_with_model(model, request_prompt)
            if patch:
                confidence_score, reason = self.confidence_manager.assign_confidence_score(error_signature, patch)

                if confidence_score is None:
                    logger.warning(f"⚠ AI did not return a confidence score for {model}. Skipping patch.")
                    continue

                # Accept patch if confidence improves
                if confidence_score > past_confidence:
                    logger.info(f"✅ AI confidence improved ({past_confidence} ➡ {confidence_score}). Patch accepted.")
                    self.confidence_manager.store_patch(error_signature, patch, confidence_score)
                    return patch

                logger.warning(f"⚠ AI confidence remains low ({confidence_score}). Skipping patch.")

        logger.error("❌ All AI models failed to generate a useful patch.")
        return None

    def save_model(self, model_name: str, model_data: Dict = None):
        """
        Saves the given model data to a JSON file.

        Args:
            model_name (str): Name of the model.
            model_data (dict, optional): Model parameters or metadata. Defaults to empty dict.
        """
        model_data = model_data or {}

        file_path = os.path.join(self.MODEL_STORAGE_DIR, f"{model_name}.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(model_data, f, indent=4)
            logger.info(f"✅ Model '{model_name}' saved successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to save model '{model_name}': {e}")

    def load_model(self, model_name: str) -> Dict:
        """
        Loads the specified model from storage.

        Args:
            model_name (str): Name of the model.

        Returns:
            dict: Loaded model data if successful, otherwise an empty dictionary.
        """
        file_path = os.path.join(self.MODEL_STORAGE_DIR, f"{model_name}.json")
        if not os.path.exists(file_path):
            logger.warning(f"⚠ Model '{model_name}' not found.")
            return {}  # Changed from None to {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                model_data = json.load(f)
            logger.info(f"✅ Model '{model_name}' loaded successfully.")
            return model_data if isinstance(model_data, dict) else {}  # Ensure it's a dictionary
        except Exception as e:
            logger.error(f"❌ Failed to load model '{model_name}': {e}")
            return {}  # Changed from None to {}


    def _format_prompt(self, error_msg: str, code_context: str, test_file: str) -> str:
        """Formats the debugging request into a structured AI prompt."""
        return (
            f"You are an expert debugging assistant.\n\n"
            f"Test File: {test_file}\n"
            f"Error Message: {error_msg}\n"
            f"Code Context:\n{code_context}\n\n"
            f"Generate a fix for the code in unified diff format (`diff --git` style)."
        )

    def _compute_error_signature(self, error_msg: str, code_context: str) -> str:
        """
        Computes a unique signature for the given error and code context.
        Used to track and avoid repeating similar patches.
        """
        combined = error_msg + code_context
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def _generate_with_model(self, model: str, prompt: str) -> Optional[str]:
        """Dynamically calls the appropriate AI model."""
        if model == "openai":
            if not self.openai_api_key:
                logger.error("OpenAI API key not set.")
                return None
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert debugging assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                patch = response.choices[0].message.content.strip()
                return patch
            except Exception as e:
                logger.exception(f"OpenAI API call failed: {e}")
                return None

        elif model in ["mistral", "deepseek"]:
            try:
                return self._simulate_model_response(model, prompt)
            except Exception as e:
                logger.exception(f"{model} model failed: {e}")
                return None

        else:
            logger.error(f"Unsupported model: {model}")
            return None

    def _simulate_model_response(self, model: str, prompt: str) -> str:
        """
        Simulate a model response for debugging purposes.
        In a real-world scenario, integrate with the actual model API.
        """
        logger.debug(f"Simulating response for {model} with prompt: {prompt}")
        return f"--- simulated patch from {model}\n+++ patched code"
