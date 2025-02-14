# agents/core/JournalAgent.py
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from agents.core.utilities.AgentBase import AgentBase  # Using AgentBase instead of IAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class JournalAgent(AgentBase):
    """
    Specialized agent for managing journal entries, extending AgentBase.
    """

    def __init__(self, journal_directory: str = "journals"):
        """
        Initializes the JournalAgent with a storage directory for journal entries.

        Args:
            journal_directory (str): Directory where journal entries are stored.
        """
        super().__init__(name="JournalAgent", project_name="AI_Journal_Manager")
        self.journal_directory = journal_directory
        os.makedirs(self.journal_directory, exist_ok=True)
        logger.info(f"JournalAgent initialized. Using directory: {self.journal_directory}")

    def describe_capabilities(self) -> str:
        """Return a description of this agent's responsibilities."""
        return "Handles journal creation, editing, retrieval, listing, and deletion."

    def create_journal_entry(self, title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
        """
        Creates a new journal entry and saves it as a JSON file.

        Args:
            title (str): Title of the journal entry.
            content (str): Content of the journal entry.
            tags (List[str], optional): Tags associated with the entry.

        Returns:
            Dict[str, Any]: Status and file path of the created journal entry.
        """
        tags = tags or []
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.journal_directory, f"{title}_{timestamp}.json")

        entry_data = {
            "title": title,
            "content": content,
            "tags": tags,
            "timestamp": timestamp
        }

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(entry_data, f, indent=4)
            logger.info(f"Journal entry '{title}' created at {filename}.")
            return {"status": "success", "file_path": filename, "timestamp": timestamp}
        except IOError as e:
            logger.error(f"Failed to create journal entry '{title}': {e}")
            return {"status": "error", "message": f"Could not create entry '{title}'"}

    def retrieve_journal_entry(self, title: str) -> Dict[str, Any]:
        """
        Retrieves an existing journal entry by title.

        Args:
            title (str): Title of the journal entry to retrieve.

        Returns:
            Dict[str, Any]: Retrieved journal entry or error message.
        """
        try:
            file_candidates = [f for f in os.listdir(self.journal_directory) if title in f]
            if not file_candidates:
                return {"status": "error", "message": f"No journal entry found with title '{title}'"}

            filepath = os.path.join(self.journal_directory, file_candidates[0])
            with open(filepath, "r", encoding="utf-8") as f:
                entry_data = json.load(f)

            logger.info(f"Retrieved journal entry '{title}' from {filepath}.")
            return {"status": "success", "entry": entry_data}
        except (FileNotFoundError, IOError, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving journal entry '{title}': {e}")
            return {"status": "error", "message": f"Error retrieving '{title}'"}

    def update_journal_entry(self, title: str, new_content: str) -> Dict[str, Any]:
        """
        Updates an existing journal entry with new content.

        Args:
            title (str): Title of the journal entry to update.
            new_content (str): New content to update in the journal.

        Returns:
            Dict[str, Any]: Status of the update operation.
        """
        existing = self.retrieve_journal_entry(title)
        if existing.get("status") == "error":
            return existing

        entry = existing["entry"]
        entry["content"] = new_content
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.journal_directory, f"{title}_{entry['timestamp']}.json")

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=4)
            logger.info(f"Updated journal entry '{title}' with new content.")
            return {"status": "success", "file_path": filename}
        except IOError as e:
            logger.error(f"Error updating journal entry '{title}': {e}")
            return {"status": "error", "message": f"Failed to update '{title}'"}

    def delete_journal_entry(self, title: str) -> Dict[str, Any]:
        """
        Deletes a journal entry by title.

        Args:
            title (str): Title of the journal entry to delete.

        Returns:
            Dict[str, Any]: Status of the delete operation.
        """
        file_candidates = [f for f in os.listdir(self.journal_directory) if title in f]
        if not file_candidates:
            return {"status": "error", "message": f"No journal entry found with title '{title}'"}

        filepath = os.path.join(self.journal_directory, file_candidates[0])
        try:
            os.remove(filepath)
            logger.info(f"Deleted journal entry '{title}' at {filepath}.")
            return {"status": "success", "message": f"'{title}' deleted successfully."}
        except Exception as e:
            logger.error(f"Error deleting '{title}': {e}")
            return {"status": "error", "message": f"Could not delete '{title}'"}

    def list_journal_entries(self) -> Dict[str, Any]:
        """
        Lists all journal entries in the journal directory.

        Returns:
            Dict[str, Any]: List of available journal entries.
        """
        results = []
        for file in os.listdir(self.journal_directory):
            if file.endswith(".json"):
                with open(os.path.join(self.journal_directory, file), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    results.append({"title": data["title"], "timestamp": data["timestamp"]})
        logger.info(f"Listed {len(results)} journal entries.")
        return {"status": "success", "entries": results}

    def solve_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Perform a journaling action (create, retrieve, etc.).
        Returns structured dictionary responses for test clarity.

        Args:
            task (str): Action to be performed.
            **kwargs: Additional parameters.

        Returns:
            Dict[str, Any]: Result of the operation.
        """
        task_methods = {
            "create": self.create_journal_entry,
            "retrieve": self.retrieve_journal_entry,
            "update": self.update_journal_entry,
            "delete": self.delete_journal_entry,
            "list": self.list_journal_entries,
        }

        if task in task_methods:
            return task_methods[task](**kwargs)
        else:
            logger.error(f"Invalid task '{task}' requested.")
            return {"status": "error", "message": f"Invalid task '{task}'"}

    def shutdown(self) -> None:
        """
        Logs a shutdown message.
        """
        logger.info("JournalAgent is shutting down.")
