import logging
from typing import Dict, List
from ai_engine.patch_analyzer import AIPatchAnalyzer
from ai_engine.confidence_manager import AIConfidenceManager
from ai_engine.models.debugger.auto_fix_manager import AutoFixManager

logger = logging.getLogger("AIPatchRetryManager")
logger.setLevel(logging.DEBUG)

class AIPatchRetryManager:
    """
    Manages AI-assisted patch retries before rollback.

    - AI explains why a patch failed.
    - AI suggests modifications if confidence improves.
    - Automatically retries modified patches.
    - If all fails, marks patch for manual review.
    """

    CONFIDENCE_THRESHOLD = 0.2  # Minimum confidence to attempt retry
    MAX_AI_PATCH_ATTEMPTS = 2   # AI gets two additional tries before rollback

    def __init__(self, *, confidence_manager: AIConfidenceManager, auto_fix_manager: AutoFixManager, patch_analyzer: AIPatchAnalyzer):
        """
        Initializes the retry manager with injected dependencies.
        """
        self.confidence_manager = confidence_manager
        self.retry_manager = auto_fix_manager
        self.ai_analyzer = patch_analyzer

    def retry_failed_patches(self, failed_patches: Dict[str, List[str]]):
        """
        AI reviews failed patches and decides whether to retry or flag them.
        """
        for error_signature, patches in failed_patches.items():
            for patch in patches:
                # Analyze the failed patch
                reason, confidence_boost = self.ai_analyzer.analyze_failed_patch(error_signature, patch)
                logger.debug(f"Analysis for {error_signature}: {reason} with boost {confidence_boost}")

                # Retrieve current confidence and update it
                current_confidence = self.confidence_manager.calculate_confidence(error_signature)
                new_confidence = min(1.0, current_confidence + confidence_boost)
                logger.info(f"🔄 Confidence updated: {current_confidence:.2f} ➡ {new_confidence:.2f} for {error_signature}")

                if new_confidence >= self.CONFIDENCE_THRESHOLD:
                    logger.info(f"🛠️ AI suggests retrying patch for {error_signature}.")
                    modified_patch = self.ai_analyzer.modify_failed_patch(error_signature, patch)
                    # Use the wrapper method on AutoFixManager to apply the patch.
                    patch_success = self.retry_manager.apply_patch(modified_patch)

                    if patch_success:
                        logger.info(f"✅ AI-modified patch for {error_signature} worked!")
                        # Optionally update a learning database or other state here
                    else:
                        logger.warning(f"❌ AI-modified patch failed for {error_signature}.")
                else:
                    logger.error(f"🚨 AI confidence remains low. Marking {error_signature} for manual review.")
