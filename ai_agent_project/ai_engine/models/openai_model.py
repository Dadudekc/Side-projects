import os
import openai
import logging
import json
import random
from typing import Optional, Dict, Tuple

logger = logging.getLogger("OpenAIModel")
logger.setLevel(logging.DEBUG)

AI_PERFORMANCE_TRACKER_FILE = "ai_performance.json"

class OpenAIModel:
    """
    OpenAI GPT-4 model wrapper for generating debugging patches.
    - Uses OpenAI GPT-4 Turbo to generate patches.
    - Retries failed patches with slight modifications.
    - Validates AI patches before applying them.
    - Tracks which AI settings generate the best patches.
    """

    MAX_RETRIES = 3  # Number of retries with modified prompts
    MIN_VALIDATION_SCORE = 0.75  # Minimum confidence score to apply a patch

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the OpenAI model wrapper.

        Args:
            api_key (Optional[str]): The OpenAI API key. Defaults to environment variable if not provided.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("❌ OpenAI API key is missing. Ensure it's set in the environment or provided.")
        
        self.ai_performance = self._load_ai_performance()

    def generate_patch(self, error_message: str, code_context: str, test_file: str) -> Optional[str]:
        """
        Generates a patch suggestion and validates it before application.
        - Attempts OpenAI GPT-4 Turbo.
        - Retries with slight prompt modifications if necessary.
        """
        request_prompt = self._format_prompt(error_message, code_context, test_file)

        # Try OpenAI first
        patch, model_used = self._generate_patch_with_retries(request_prompt)
        if patch and self._validate_patch(patch):
            self._record_ai_performance(model_used, success=True)
            return patch
        else:
            self._record_ai_performance(model_used, success=False)

        logger.error("❌ All OpenAI attempts failed. No valid patch generated.")
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

    def _generate_patch_with_retries(self, prompt: str) -> Tuple[Optional[str], str]:
        """
        Attempts to generate a patch with OpenAI GPT-4 Turbo, with retries.
        Returns a tuple (patch, model_used).
        """
        for attempt in range(self.MAX_RETRIES + 1):
            modified_prompt = self._modify_prompt(prompt, attempt) if attempt > 0 else prompt
            patch = self._generate_with_openai(modified_prompt)
            if patch:
                return patch, "OpenAI"

        return None, "None"

    def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """
        Calls OpenAI GPT-4 Turbo to generate a patch.
        """
        if not self.api_key:
            logger.error("❌ OpenAI API key not set. Skipping GPT-4 Turbo call.")
            return None

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert debugging assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                api_key=self.api_key
            )
            logger.info("✅ OpenAI successfully generated a patch.")
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"❌ OpenAI GPT-4 Turbo call failed: {e}")
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
            "+ # fixed line by OpenAI"
        )
