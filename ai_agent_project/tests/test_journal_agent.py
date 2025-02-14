import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class JournalAgent:
    """
    A specialized agent for managing journal entries.
    Provides functions for creating, retrieving, updating, and deleting logs.
    """

    def __init__(self, journal_directory: str = "journals"):
        """
        Initializes the JournalAgent with a default directory for storing journal entries.

        Args:
            journal_directory (str): Directory where journal entries are stored.
        """
        self.journal_directory = journal_directory
        os.makedirs(self.journal_directory, exist_ok=True)
        logger.info(f"JournalAgent initialized. Using directory: {self.journal_directory}")

    def create_journal_entry(self, title: str, content: str, tags: List[str] = None) -> Dict[str, Any]:
        """Creates a new journal entry with title, content, and optional tags."""
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
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(entry_data, file, indent=4)
            logger.info(f"Journal entry '{title}' created at {filename}.")
            return {"file_path": filename, "timestamp": timestamp}
        except IOError as e:
            logger.error(f"Failed to create journal entry '{title}': {e}")
            return {"error": f"Failed to create entry '{title}'"}

    def retrieve_journal_entry(self, title: str) -> Dict[str, Any]:
        """Retrieves a journal entry by title."""
        try:
            matching_files = [f for f in os.listdir(self.journal_directory) if title in f]
            if not matching_files:
                raise FileNotFoundError(f"No journal entry found with title '{title}'")

            filepath = os.path.join(self.journal_directory, matching_files[0])
            with open(filepath, "r", encoding="utf-8") as file:
                entry_data = json.load(file)

            logger.info(f"Retrieved journal entry '{title}' from {filepath}.")
            return entry_data
        except (FileNotFoundError, IOError, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving journal entry '{title}': {e}")
            return {"error": f"Error retrieving entry '{title}'"}

    def update_journal_entry(self, title: str, new_content: str) -> Dict[str, Any]:
        """Updates an existing journal entry with new content."""
        entry = self.retrieve_journal_entry(title)
        if "error" in entry:
            return entry

        entry["content"] = new_content
        entry["timestamp"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.journal_directory, f"{title}_{entry['timestamp']}.json")

        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(entry, file, indent=4)
            logger.info(f"Updated journal entry '{title}' at {filename}.")
            return {"message": f"Journal entry '{title}' updated successfully.", "file_path": filename}
        except IOError as e:
            logger.error(f"Error updating journal entry '{title}': {e}")
            return {"error": f"Error updating entry '{title}'"}

    def delete_journal_entry(self, title: str) -> Dict[str, str]:
        """Deletes a journal entry by title."""
        try:
            matching_files = [f for f in os.listdir(self.journal_directory) if title in f]
            if not matching_files:
                raise FileNotFoundError(f"No journal entry found with title '{title}'.")

            filepath = os.path.join(self.journal_directory, matching_files[0])
            os.remove(filepath)
            logger.info(f"Deleted journal entry '{title}' at {filepath}.")
            return {"message": f"Journal entry '{title}' deleted successfully."}
        except (FileNotFoundError, IOError) as e:
            logger.error(f"Error deleting journal entry '{title}': {e}")
            return {"error": f"Error deleting entry '{title}'"}

    def list_journal_entries(self) -> List[Dict[str, str]]:
        """Lists all journal entries in the journal directory."""
        entries = []
        for filename in os.listdir(self.journal_directory):
            if filename.endswith(".json"):
                with open(os.path.join(self.journal_directory, filename), "r", encoding="utf-8") as file:
                    entry_data = json.load(file)
                    entries.append({"title": entry_data["title"], "timestamp": entry_data["timestamp"]})

        logger.info(f"Listed {len(entries)} journal entries.")
        return entries

    def perform_task(self, task_data: Dict[str, Any]) -> str:
        """
        Executes a journal-related task based on task_data.

        Args:
            task_data (Dict[str, Any]): Information necessary for the task execution.

        Returns:
            str: Outcome of the task.
        """
        action = task_data.get("action")
        title = task_data.get("title", "Untitled Entry")
        content = task_data.get("content", "")
        tags = task_data.get("tags", [])

        if action == "create":
            response = self.create_journal_entry(title, content, tags)
            return f"Journal entry '{title}' created at {response.get('file_path', 'Unknown path')}"

        elif action == "retrieve":
            entry = self.retrieve_journal_entry(title)
            return f"Retrieved entry: {entry}" if "error" not in entry else entry["error"]

        elif action == "update":
            new_content = task_data.get("new_content", content)
            response = self.update_journal_entry(title, new_content)
            return response.get("message", response.get("error"))

        elif action == "delete":
            response = self.delete_journal_entry(title)
            return response.get("message", response.get("error"))

        elif action == "list":
            entries = self.list_journal_entries()
            return f"Journal entries: {entries}"

        else:
            return "Invalid action specified."


# ✅ Example Usage for Debugging
if __name__ == "__main__":
    agent = JournalAgent(journal_directory="test_journals")

    # Create a new journal entry
    print(agent.perform_task({"action": "create", "title": "Debugging Test", "content": "Testing JournalAgent integration."}))

    # List current entries
    print(agent.perform_task({"action": "list"}))

    # Retrieve the journal entry
    print(agent.perform_task({"action": "retrieve", "title": "Debugging Test"}))

    # Update the journal entry
    print(agent.perform_task({"action": "update", "title": "Debugging Test", "new_content": "Updated content."}))

    # Retrieve again
    print(agent.perform_task({"action": "retrieve", "title": "Debugging Test"}))

    # Delete the entry
    print(agent.perform_task({"action": "delete", "title": "Debugging Test"}))

    # Verify deletion
    print(agent.perform_task({"action": "list"}))
