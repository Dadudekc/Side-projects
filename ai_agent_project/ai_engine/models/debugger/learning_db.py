import json
import os
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("LearningDB")


class LearningDB:
    """
    Stores previously encountered errors and fixes.
    """

    DB_FILE = "learning_db.json"

    def __init__(self):
        self.data = self.load_db()

    def load_db(self) -> Dict[str, Any]:
        """Loads the learning database."""
        if os.path.exists(self.DB_FILE):
            with open(self.DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_signature(self, error: Dict[str, str]) -> str:
        """Creates a hash signature for the error."""
        return hash(error["error_message"])

    def get_known_fix(self, error_sig: str) -> Optional[str]:
        """Returns a known fix for an error signature if available."""
        return self.data.get(error_sig, {}).get("patch")

    def update(self, error_sig: str, patch: str, success: bool):
        """Updates the learning database."""
        self.data[error_sig] = {"patch": patch, "success": success}
        with open(self.DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)
