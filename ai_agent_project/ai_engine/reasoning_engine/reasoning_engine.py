"""

This class implements an advanced reasoning engine that utilizes a rule-based logical inference model. It also features a cache mechanism to optimize performance. The reasoning engine is used to perform reasoning on the given prompts and it returns the response.

Attributes:
    logger (Logger): Logging object instance.
    cache_enabled (bool): flag that defines whether to store the reasoning results or not.
    cache (dict): Dictionary to store the results of the inference.
    reasoning_model (RuleBasedReasoning): object instance of
"""

import logging
import hashlib
from typing import Dict, Any
from ai_engine.reasoning_engine.rule_based_reasoning import RuleBasedReasoning

class ReasoningEngine:
    """
    Advanced reasoning engine that performs structured logical inference.

    Features:
      - Rule-based logic inference.
      - Caching to optimize performance.
      - Modular design that can be extended with additional strategies.
    """

    def __init__(self, cache_enabled: bool = True):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cache_enabled = cache_enabled
        self.cache: Dict[str, Any] = {}
        self.reasoning_model = RuleBasedReasoning()
        self.logger.debug("ReasoningEngine initialized with caching=%s", cache_enabled)

    def _cache_key(self, prompt: str) -> str:
        # Create a unique key using an MD5 hash of the prompt.
        return hashlib.md5(prompt.encode("utf-8")).hexdigest()

    def reason(self, prompt: str) -> str:
        """
        Performs reasoning on the given prompt using the integrated rule-based model.
        """
        self.logger.debug("Processing prompt: %s", prompt)
        cache_key = self._cache_key(prompt)
        if self.cache_enabled and cache_key in self.cache:
            self.logger.debug("Returning cached result for key: %s", cache_key)
            return self.cache[cache_key]

        response = self.reasoning_model.reason(prompt)
        if self.cache_enabled:
            self.cache[cache_key] = response
        return response
