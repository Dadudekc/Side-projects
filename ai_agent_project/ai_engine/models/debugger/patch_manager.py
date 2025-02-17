import logging
from typing import Optional, Dict, Any
from ai_engine.models.debugger.debugging_strategy import DebuggingStrategy

logger = logging.getLogger("PatchManager")


class PatchManager:
    """
    Manages patch generation and application.
    """

    def __init__(self, debug_strategy: Optional[DebuggingStrategy] = None):
        self.debug_strategy = debug_strategy

    def apply_fix(self, failure: Dict[str, str]) -> bool:
        """Applies a fix for a test failure."""
        if self.debug_strategy:
            patch = self.debug_strategy.generate_patch(failure["error"], failure["file"])
            return self.debug_strategy.apply_patch(patch)
        return False
