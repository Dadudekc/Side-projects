"""

This module defines the LearningDB class which is responsible for managing a JSON database that tracks encountered errors and their respective fixes. The class is capable of loading and saving the database from/to a file, as well as performing operations like storing a new fix or searching for an existing fix based on an error message.

The LearningDB class has the following attributes:
- DB_FILE: A string that represents the name of the database file.
- data: A dictionary that holds the content of the database.

The
"""

import json
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("LearningDB")

class LearningDB:
    """
    Stores previously encountered errors and fixes in a JSON database.
    """

    DB_FILE = "learning_db.json"

    def __init__(self):
        self.data = self._load_db()

    def _load_db(self) -> Dict[str, Any]:
        """Loads the learning database from file, creating one if necessary."""
        if os.path.exists(self.DB_FILE):
            try:
                with open(self.DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning("⚠️ Corrupted learning_db.json detected. Resetting database.")
                return {}
        return {}

    def search_learned_fix(self, error_message: str) -> Optional[str]:
        """
        Retrieves a previously learned fix for a given error message.
        """
        return self.data.get(error_message, {}).get("patch")

    def store_fix(self, error_message: str, patch: str):
        """
        Stores a successful fix in the learning database.
        """
        self.data[error_message] = {"patch": patch, "success": True}
        self._save_db()

    def _save_db(self):
        """Saves the learning database to a file."""
        try:
            with open(self.DB_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            logger.info("✅ Learning database updated successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to save learning database: {e}")

# Auto-initialize learning DB if needed
if __name__ == "__main__":
    db = LearningDB()
    print("🗃️ Learning Database Initialized")
