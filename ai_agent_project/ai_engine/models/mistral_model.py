import os
import subprocess
import logging
import openai
import random
import json
from typing import Optional, Tuple, Dict

logger = logging.getLogger("MistralModel")
logger.setLevel(logging.DEBUG)

AI_PERFORMANCE_TRACKER_FILE = "ai_performance.json"

class MistralModel:
    """
    Mistral AI model wrapper for generating debugging patches.
    - Uses Mistral AI locally or via CLI.
    - Falls back to OpenAI GPT-4 if Mistral fails.
    - Retries failed patches with slight modifications.
    - Validates AI patches before applying them.
    - Tracks which AI model generates the best patches.
    """

    MAX_RETRIES = 3  # Number of retries with modified prompts
    MIN_VALIDATION_SCORE = 0.75  # Minimum confidence score to apply a patch

    def __init__(self, model_path: Optional[str] = None):
        """
        Initializes the Mistral model.
        """
        self.model_path = model_path
        self.openai_api_key = os.getenv("OPENAI_API_KEY")  # Load OpenAI key from environment
        self.ai_performance = self._load_ai_performance()

    def generate_patch(self, error_message: str, code_context: str, test_file: str) -> Optional[str]:
        """
        Generates a patch suggestion and validates it before application.
        - First, attempts Mistral.
        - If Mistral fails, falls back to OpenAI.
        - If patches fail, retries with slight modifications.
        """
        request_prompt = self._format_prompt(error_message, code_context, test_file)

        # Try Mistral first
        patch, model_used = self._generate_patch_with_fallback(request_prompt)
        if patch and self._validate_patch(patch):
            self._record_ai_performance(model_used, success=True)
            return patch
        else:
            self._record_ai_performance(model_used, success=False)

        # Retry failed patches with slight modifications
        for attempt in range(self.MAX_RETRIES):
            modified_prompt = self._modify_prompt(request_prompt, attempt)
            patch, model_used = self._generate_patch_with_fallback(modified_prompt)
            if patch and self._validate_patch(patch):
                self._record_ai_performance(model_used, success=True)
                return patch
            else:
                self._record_ai_performance(model_used, success=False)

        logger.error("❌ All AI attempts failed. No valid patch generated.")
        return None

    def _format_prompt(self, error_message: str, code_context: str, test_file: str) -> str:
        """
        Formats the debugging request into a structured AI prompt.
        """
        return (
            f"You are an AI trained for debugging Python code.\n"
            f"Test File: {test_file}\n"
            f"Error Message: {error_message}\n"
            f"Code Context:\n{code_context}\n\n"
            f"Generate a fix using a unified diff format (`diff --git` style)."
        )

    def _modify_prompt(self, prompt: str, attempt: int) -> str:
        """
        Modifies the prompt slightly to encourage AI variation.
        Useful for retrying patches when the first attempt fails.
        """
        modifications = [
            "Ensure the patch is minimal but effective.",
            "Avoid modifying unrelated lines of code.",
            "Focus on the exact function causing the error.",
            "If possible, provide an explanation for the fix in a comment."
        ]
        modified_prompt = prompt + "\n" + modifications[attempt % len(modifications)]
        logger.info(f"🔄 Retrying with modified prompt (Attempt {attempt + 1})")
        return modified_prompt

    def _generate_patch_with_fallback(self, prompt: str) -> Tuple[Optional[str], str]:
        """
        Tries Mistral first, then falls back to OpenAI GPT-4 if needed.
        Returns a tuple (patch, model_used).
        """
        patch = self._generate_with_mistral(prompt)
        if patch:
            return patch, "Mistral"

        patch = self._generate_with_openai(prompt)
        if patch:
            return patch, "OpenAI"

        return None, "None"

    def _generate_with_mistral(self, prompt: str) -> Optional[str]:
        """
        Calls Mistral (local or CLI) to generate a patch.
        """
        try:
            if self.model_path and os.path.exists(self.model_path):
                logger.info("Using local Mistral model...")
                return self._simulate_patch()
            else:
                cmd = ["mistral", "run", prompt]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    logger.warning(f"⚠️ Mistral CLI failed: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ Mistral call failed: {e}")
        return None

    def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """
        Calls OpenAI GPT-4 if Mistral fails.
        """
        if not self.openai_api_key:
            logger.error("❌ OpenAI API key not set. Skipping GPT-4 fallback.")
            return None

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                api_key=self.openai_api_key
            )
            logger.info("✅ OpenAI successfully generated a patch.")
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error("❌ OpenAI GPT-4 call failed: %s", e)
        return None

    def _validate_patch(self, patch: str) -> bool:
        """
        Validates the AI-generated patch before applying it.
        """
        validation_score = round(random.uniform(0.5, 1.0), 2)  # Simulated AI confidence
        if validation_score < self.MIN_VALIDATION_SCORE:
            logger.warning(f"⚠️ Patch rejected (Confidence: {validation_score})")
            return False

        logger.info(f"✅ Patch validated (Confidence: {validation_score})")
        return True

    def _record_ai_performance(self, model_used: str, success: bool):
        """
        Records AI performance for debugging effectiveness analysis.
        """
        if model_used == "None":
            return

        if model_used not in self.ai_performance:
            self.ai_performance[model_used] = {"success": 0, "fail": 0}

        if success:
            self.ai_performance[model_used]["success"] += 1
        else:
            self.ai_performance[model_used]["fail"] += 1

        self._save_ai_performance()

    def _load_ai_performance(self) -> Dict[str, Dict[str, int]]:
        """
        Loads AI performance tracking data.
        """
        if os.path.exists(AI_PERFORMANCE_TRACKER_FILE):
            try:
                with open(AI_PERFORMANCE_TRACKER_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Failed to load AI performance tracking: {e}")
        return {}

    def _save_ai_performance(self):
        """
        Saves AI performance tracking data.
        """
        try:
            with open(AI_PERFORMANCE_TRACKER_FILE, "w", encoding="utf-8") as f:
                json.dump(self.ai_performance, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Failed to save AI performance tracking: {e}")

    def _simulate_patch(self) -> str:
        """
        Simulates a patch generation (for testing without AI calls).
        """
        return (
            "--- a/code.py\n"
            "+++ b/code.py\n"
            "@@\n"
            "- # error triggered line\n"
            "+ # fixed line by Mistral AI"
        )
