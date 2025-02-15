import json
import logging
from collections import deque
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MemoryManager:
    """
    Manages short-term memory for AI agents, tracking past interactions and task history.
    """

    def __init__(self, memory_limit: int = 50):
        """
        Initializes the Memory Manager.

        Args:
            memory_limit (int): Maximum number of memory entries to store.
        """
        self.memory = deque(maxlen=memory_limit)

    def store_memory(self, key: str, value: Any) -> None:
        """
        Stores a key-value pair in memory.

        Args:
            key (str): Identifier for the memory entry.
            value (Any): Data to store.
        """
        self.memory.append({key: value})
        logger.debug(f"Stored memory: {key} -> {value}")

    def retrieve_memory(self, key: str) -> Optional[Any]:
        """
        Retrieves stored memory based on a key.

        Args:
            key (str): Identifier for the memory entry.

        Returns:
            Optional[Any]: Retrieved data, or None if key not found.
        """
        for entry in reversed(self.memory):
            if key in entry:
                logger.debug(f"Retrieved memory for {key}: {entry[key]}")
                return entry[key]
        logger.warning(f"No memory found for key: {key}")
        return None

    def clear_memory(self) -> None:
        """
        Clears all stored memory.
        """
        self.memory.clear()
        logger.info("Memory cleared.")

    def export_memory(self, filepath: str) -> None:
        """
        Exports stored memory to a JSON file.

        Args:
            filepath (str): File path to save memory data.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(list(self.memory), f, indent=4)
        logger.info(f"Memory exported to {filepath}")

    def import_memory(self, filepath: str) -> None:
        """
        Imports stored memory from a JSON file.

        Args:
            filepath (str): File path to load memory data.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                items = json.load(f)
            for entry in items:
                self.memory.append(entry)
            logger.info(f"Memory imported from {filepath}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error importing memory: {e}")
