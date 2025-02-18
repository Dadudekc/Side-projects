"""

This module implements a centralized global memory system with the class 'ContextManager'. This class uses the deque collection to store and manage information. It has methods for preprocessing text (tokenizing and stopwords removal), storing and retrieving data based on text similarity using a key-value logic, saving and loading memory items from a JSON file for persistence, and clearing the global memory. 

The module also sets up a logger to record events at the debug level and downloads the required nltk resources if not already available. An
"""

import json
import logging
from collections import deque
from typing import Dict, Any, Optional
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from difflib import SequenceMatcher

# Ensure necessary resources are downloaded
nltk.download("punkt")
nltk.download("stopwords")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ContextManager:
    """
    Centralized memory for all agents to share user preferences, responses, and contextual learning.
    """

    def __init__(self, memory_limit: int = 200, memory_file: str = "context_memory.json"):
        """
        Initializes the global memory system.

        Args:
            memory_limit (int): Maximum memory entries to retain.
            memory_file (str): File path for persistent storage.
        """
        self.memory = deque(maxlen=memory_limit)
        self.memory_file = memory_file
        self.stop_words = set(stopwords.words("english"))
        self.load_memory()

    def preprocess_text(self, text: str) -> str:
        """
        Prepares text for memory storage by tokenizing and removing stopwords.

        Args:
            text (str): The input text.

        Returns:
            str: Processed text.
        """
        tokens = word_tokenize(text.lower())
        filtered_tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        return " ".join(filtered_tokens)

    def store_memory(self, key: str, value: Any) -> None:
        """
        Stores key-value pairs in memory for global reference.

        Args:
            key (str): Identifier for memory entry.
            value (Any): Data to store.
        """
        processed_key = self.preprocess_text(key)
        self.memory.append({processed_key: value})
        self.save_memory()
        logger.debug(f"Stored in global context: {key} -> {value}")

    def retrieve_memory(self, key: str) -> Optional[Any]:
        """
        Retrieves memory based on text similarity.

        Args:
            key (str): The user's query.

        Returns:
            Optional[Any]: The most relevant memory match, or None if not found.
        """
        processed_key = self.preprocess_text(key)
        best_match = None
        best_score = 0

        for entry in reversed(self.memory):
            stored_key = list(entry.keys())[0]
            similarity = SequenceMatcher(None, processed_key, stored_key).ratio()
            if similarity > best_score and similarity > 0.75:  # Threshold for similarity match
                best_match = entry[stored_key]
                best_score = similarity

        if best_match:
            logger.debug(f"Memory retrieved for '{key}': {best_match}")
        else:
            logger.warning(f"No memory found for '{key}'")

        return best_match

    def save_memory(self) -> None:
        """
        Saves the memory state to a file for persistence.
        """
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(list(self.memory), f, indent=4)
        logger.info(f"Memory saved to {self.memory_file}")

    def load_memory(self) -> None:
        """
        Loads memory from a file.
        """
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                items = json.load(f)
            for entry in items:
                self.memory.append(entry)
            logger.info(f"Memory loaded from {self.memory_file}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading memory: {e}")

    def clear_memory(self) -> None:
        """
        Clears the global memory.
        """
        self.memory.clear()
        self.save_memory()
        logger.info("Global memory cleared.")


# Singleton Instance for Global Access
global_context = ContextManager()
