# Path: ai_agent_project/src/agents/core/utilities/ai_cache.py

import json
import os
import asyncio
import logging
from typing import Dict

class AICache:
    """
    Simple JSON-based cache for AI-generated fix suggestions.
    """

    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, str]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                self.logger.info("AI cache loaded successfully.")
            except Exception as e:
                self.logger.error(f"Failed to load AI cache: {str(e)}")
                self.cache = {}
        else:
            self.cache = {}
            self.logger.info("No existing AI cache found. Starting fresh.")

    async def get_fix(self, ai_model: str, error_type: str, error_message: str) -> str:
        key = f"{ai_model}_{error_type}_{error_message}"
        return self.cache.get(key, "")

    def set_fix(self, ai_model: str, error_type: str, error_message: str, fix: str):
        key = f"{ai_model}_{error_type}_{error_message}"
        self.cache[key] = fix

    def save_cache(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=4)
            self.logger.info("AI cache saved successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save AI cache: {str(e)}")
