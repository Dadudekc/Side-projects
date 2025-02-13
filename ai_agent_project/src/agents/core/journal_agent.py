# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\agents\tasks\journal_agent.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# Defines the `JournalAgent` class, an agent responsible for creating,
# organizing, and managing journal entries. It assists in capturing debugging logs, 
# session summaries, and user reflections, contributing to enhanced traceability 
# and knowledge retention.
#
# Classes:
# - JournalAgent: Extends `AgentBase` to provide task-specific methods 
#   for journal creation, organization, and data export.
#
# Usage:
# This module is instantiated and managed by the core agent dispatcher
# in the AI_Debugger_Assistant project.
# -------------------------------------------------------------------

import os
import datetime
import json
import logging
from typing import List, Dict, Optional, Any
from ai_agent_project.src.agents.core.utilities.agent_base import AgentBase  # Adjust path as necessary

logger = logging.getLogger(__name__)

class JournalAgent(AgentBase):
    """
    An agent specialized in creating and managing journal entries.
    Provides functions for saving logs, reflections, and summaries
    related to debugging and development tasks.
    """
    
    def __init__(self, name="JournalAgent", description="Agent for managing journal entries and logs"):
        """
        Initializes the JournalAgent with default parameters.
        
        Args:
            name (str): The agent's name.
            description (str): A short description of the agent's purpose.
        """
        super().__init__(name, description)
        self.journal_directory = "journals"  # Default directory for journal entries
        os.makedirs(self.journal_directory, exist_ok=True)
        logger.info(f"{self.name} initialized for journal management.")

    def create_journal_entry(self, title: str, content: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Creates a new journal entry with title, content, and optional tags.

        Args:
            title (str): The title of the journal entry.
            content (str): The main content of the journal entry.
            tags (Optional[List[str]]): Tags associated with the entry.

        Returns:
            Dict[str, Any]: Metadata of the created entry, including file path and timestamp.
        """
        tags = tags or []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
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
        """
        Retrieves a journal entry by title from the journal directory.

        Args:
            title (str): Title of the journal entry to retrieve.

        Returns:
            Dict[str, Any]: The content of the journal entry if found, otherwise an error message.
        """
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
            error_message = f"Error retrieving journal entry '{title}': {str(e)}"
            logger.error(error_message)
            return {"error": error_message}

    def update_journal_entry(self, title: str, new_content: str) -> Dict[str, Any]:
        """
        Updates an existing journal entry with new content.

        Args:
            title (str): Title of the journal entry to update.
            new_content (str): New content to update in the journal entry.

        Returns:
            Dict[str, Any]: Success message with the updated timestamp or error message.
        """
        entry = self.retrieve_journal_entry(title)
        if "error" in entry:
            return entry

        entry["content"] = new_content
        entry["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.journal_directory, f"{title}_{entry['timestamp']}.json")
        
        try:
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(entry, file, indent=4)
            logger.info(f"Updated journal entry '{title}' with new content at {filename}.")
            return {"message": f"Journal entry '{title}' updated successfully.", "file_path": filename}
        except IOError as e:
            error_message = f"Error updating journal entry '{title}': {str(e)}"
            logger.error(error_message)
            return {"error": error_message}

    def delete_journal_entry(self, title: str) -> Dict[str, str]:
        """
        Deletes a journal entry by title.

        Args:
            title (str): Title of the journal entry to delete.

        Returns:
            Dict[str, str]: Success or error message.
        """
        try:
            matching_files = [f for f in os.listdir(self.journal_directory) if title in f]
            if not matching_files:
                raise FileNotFoundError(f"No journal entry found with title '{title}'.")

            filepath = os.path.join(self.journal_directory, matching_files[0])
            os.remove(filepath)
            logger.info(f"Deleted journal entry '{title}' at {filepath}.")
            return {"message": f"Journal entry '{title}' deleted successfully."}
        except (FileNotFoundError, IOError) as e:
            error_message = f"Error deleting journal entry '{title}': {str(e)}"
            logger.error(error_message)
            return {"error": error_message}

    def list_journal_entries(self) -> List[Dict[str, str]]:
        """
        Lists all journal entries in the journal directory.

        Returns:
            List[Dict[str, str]]: A list of journal entry metadata including titles and timestamps.
        """
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
            task_data (Dict[str, Any]): Information necessary for the task execution, with keys like "action", "title", etc.

        Returns:
            str: Outcome of the task.
        """
        action = task_data.get("action")
        title = task_data.get("title", "Untitled Entry")
        content = task_data.get("content", "")
        tags = task_data.get("tags", [])
        
        if action == "create":
            response = self.create_journal_entry(title, content, tags)
            return response.get("message", f"Journal entry '{title}' created.")
        
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

# Example usage (testing purposes)
if __name__ == "__main__":
    journal_agent = JournalAgent()
    journal_agent.create_journal_entry("Debugging Session", "Fixed bug in login system", tags=["debugging", "login"])
    print("Current Entries:", journal_agent.list_journal_entries())

# -------------------------------------------------------------------
# Future Improvements
# -------------------------------------------------------------------
# 1. **Auto-Tagging with NLP**:
#    Integrate NLP to analyze journal content, suggesting or automatically adding relevant tags
#    for improved organization and searchability.
#
# 2. **Search and Filter Capabilities**:
#    Add advanced search and filtering options based on tags, timestamps, and keywords within 
#    content to enhance retrieval of specific journal entries.
#
# 3. **Journal Summarization and Insights**:
#    Implement a summarization feature to generate concise summaries for each entry and provide 
#    monthly or project-based insights, enhancing retrospective analysis.
#
# 4. **Enhanced Error Logging**:
#    Extend logging to include structured JSON logs, integrating with external logging tools or 
#    databases for better traceability and issue resolution.
#
# 5. **Scheduled Entry Backups**:
#    Add automated periodic backups for entries, ensuring data persistence and recovery options 
#    in case of data loss.
#
# -------------------------------------------------------------------
