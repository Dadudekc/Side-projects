import logging
from typing import Dict, List
from test_retry_manager import AutoFixManager
from ai_patch_analyzer import AIPatchAnalyzer
from ai_confidence_manager import AIConfidenceManager

logger = logging.getLogger("AIPatchRetryManager")
logger.setLevel(logging.DEBUG)

class AIPatchRetryManager:
    """
    Handles AI-assisted patch retries before rollback.
    - AI explains why a patch failed.
    - AI suggests modifications if confidence improves.
    - Automatically retries modified patches.
    - If all fails, marks patch for manual review.
    """

    MAX_AI_PATCH_ATTEMPTS = 2  # AI gets two additional tries before rollback

    def __init__(self):
        self.retry_manager = AutoFixManager()
        self.ai_analyzer = AIPatchAnalyzer()
        self.confidence_manager = AIConfidenceManager()
        self.failed_patches = {}

    def retry_failed_patches(self, failed_patches: Dict[str, List[str]]):
        """
        AI reviews failed patches and decides whether to retry or flag them.
        """
        for error_signature, patches in failed_patches.items():
            for patch in patches:
                reason, confidence_boost = self.ai_analyzer.analyze_failed_patch(error_signature, patch)

                current_confidence = self.confidence_manager.get_confidence(error_signature)
                new_confidence = min(1.0, current_confidence + confidence_boost)  # Keep confidence ≤ 1.0

                logger.info(f"🔄 Confidence updated: {current_confidence} ➡ {new_confidence} for {error_signature}")

                if new_confidence >= 0.7:
                    logger.info(f"🛠️ AI suggests retrying patch for {error_signature}.")
                    modified_patch = self.ai_analyzer.modify_failed_patch(error_signature, patch)
                    patch_success = self.retry_manager.debugging_strategy.apply_patch(modified_patch)

                    if patch_success:
                        logger.info(f"✅ AI-modified patch for {error_signature} worked!")
                        self.retry_manager.debugging_strategy.learning_db[error_signature] = {
                            "patch": modified_patch, "success": True
                        }
                        self.retry_manager.debugging_strategy._save_learning_db()
                    else:
                        logger.warning(f"❌ AI-modified patch failed for {error_signature}.")
                else:
                    logger.error(f"🚨 AI confidence remains low. Marking {error_signature} for manual review.")
