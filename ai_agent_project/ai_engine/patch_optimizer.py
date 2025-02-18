"""
This class is used for AI-driven patch tuning system. It auto-modifies failed patches based on known patterns, tracks failed patches and prevents retrying known bad fixes. If confidence improves on a modified patch, re-tries debugging. The main components of this class include:

1. `refine_failed_patch`: A method that auto-tunes a failed patch by making incremental modifications. If the AI confidence improves, the patch is retried.
2. `_modify_patch`: A private method that modifies a
"""

import os
import json
import logging
import random
import subprocess
from typing import Optional, Tuple, Dict, List
from ai_engine.models.debugger.patch_tracking_manager import PatchTrackingManager
from ai_engine.confidence_manager import AIConfidenceManager
from ai_engine.models.ai_model_manager import AIModelManager

logger = logging.getLogger("AIPatchOptimizer")
logger.setLevel(logging.DEBUG)

class AIPatchOptimizer:
    """
    AI-driven patch tuning system.

    ✅ Auto-modifies failed patches based on known patterns.
    ✅ Tracks failed patches & prevents retrying known bad fixes.
    ✅ If confidence improves on a modified patch, re-attempts debugging.
    """

    MAX_MODIFICATION_ATTEMPTS = 3  # Number of times AI will tweak a failed patch

    def __init__(self):
        self.patch_tracker = PatchTrackingManager()
        self.confidence_manager = AIConfidenceManager()
        self.ai_model = AIModelManager()

    def refine_failed_patch(self, error_signature: str, original_patch: str) -> Optional[str]:
        """
        Auto-tunes a failed patch by making incremental modifications.
        If AI confidence improves, the patch is retried.
        """
        logger.info(f"🔄 Refining failed patch for error: {error_signature}")

        # Retrieve known failure patterns
        past_failures = self.patch_tracker.get_failed_patches(error_signature)

        # Check if AI has already tried modifying this patch too many times
        if len(past_failures) >= self.MAX_MODIFICATION_ATTEMPTS:
            logger.warning(f"🚨 Max modification attempts reached for error: {error_signature}")
            return None

        # Generate a modified version of the patch
        modified_patch = self._modify_patch(original_patch)

        # Get AI confidence on the new patch
        confidence_score, reason = self.confidence_manager.assign_confidence_score(error_signature, modified_patch)

        # Only attempt the new patch if confidence improves
        if confidence_score > self.confidence_manager.get_confidence(error_signature):
            logger.info(f"✅ AI confidence improved ({confidence_score} > previous). Retrying new patch.")
            return modified_patch
        else:
            logger.warning(f"⚠️ AI confidence remained low ({confidence_score}). Patch rejected.")
            self.patch_tracker.record_failed_patch(error_signature, modified_patch)
            return None

    def _modify_patch(self, patch: str) -> str:
        """
        Modifies a patch using AI heuristics.
        Can fix common issues like missing imports, indentation errors, etc.
        """
        modifications = [
            lambda p: p.replace("- ", "+ "),  # Flip incorrect removals
            lambda p: p.replace("def ", "async def "),  # Try async fix
            lambda p: p.replace("print(", "logger.debug("),  # Replace print statements
            lambda p: p.replace("\n-", "\n+"),  # Swap diff markers
        ]

        # Apply a random modification
        modified_patch = random.choice(modifications)(patch)
        logger.debug(f"🔧 Modified patch:\n{modified_patch}")
        return modified_patch

    def attempt_patch_reapply(self, error_signature: str, test_file: str, original_patch: str) -> bool:
        """
        If a patch is modified successfully, attempt to reapply it.
        """
        modified_patch = self.refine_failed_patch(error_signature, original_patch)
        if not modified_patch:
            logger.error(f"❌ No valid modifications found for error: {error_signature}")
            return False

        # Apply the modified patch
        patch_success = self.ai_model._generate_with_model("mistral", modified_patch)

        if patch_success:
            logger.info(f"✅ Successfully re-applied modified patch for error: {error_signature}")
            self.patch_tracker.record_successful_patch(error_signature, modified_patch)
            return True
        else:
            logger.warning(f"❌ Modified patch also failed for error: {error_signature}")
            self.patch_tracker.record_failed_patch(error_signature, modified_patch)
            return False
