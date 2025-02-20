# C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\agents\core\utilities\memory_manager.py

import sqlite3
import threading
import logging
from datetime import datetime, timedelta

class MemoryManager:
    def __init__(self, db_path="ai_agent_memory.db", table_name="memory_entries"):
        self.db_path = db_path
        self.table_name = table_name
        self.lock = threading.Lock()
        self._initialize_database()

    def _initialize_database(self):
        """Initialize the database and ensure the memory entries table exists."""
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            user_prompt TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_query)
                conn.commit()
            logging.info(f"Database initialized; table '{self.table_name}' is ready.")
        except sqlite3.Error as e:
            logging.error(f"Error initializing database: {e}")

    def _get_connection(self):
        """Create and return a new database connection."""
        try:
            conn = sqlite3.connect(self.db_path)
            logging.debug("Database connection established.")
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def save_memory(self, project_name: str, user_prompt: str, ai_response: str):
        """Save a memory entry into the database."""
        insert_query = f"""
        INSERT INTO {self.table_name} (project_name, user_prompt, ai_response)
        VALUES (?, ?, ?);
        """
        try:
            with self.lock, self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(insert_query, (project_name, user_prompt, ai_response))
                conn.commit()
            logging.info(f"Memory entry saved for project '{project_name}'.")
        except sqlite3.Error as e:
            logging.error(f"Failed to save memory for project '{project_name}': {e}")

    def retrieve_memory(self, project_name: str, limit: int = 5) -> str:
        """Retrieve the latest memory entries for a given project."""
        select_query = f"""
        SELECT user_prompt, ai_response FROM {self.table_name}
        WHERE project_name = ?
        ORDER BY timestamp DESC
        LIMIT ?;
        """
        try:
            with self.lock, self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(select_query, (project_name, limit))
                rows = cursor.fetchall()
            
            memory_context = "\n".join(f"User: {user}\nAI: {response}" for user, response in rows[::-1])
            logging.info(f"Retrieved {len(rows)} memory entries for project '{project_name}'.")
            return memory_context
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve memory for project '{project_name}': {e}")
            return ""

    def delete_memory_older_than(self, project_name: str, days: int):
        """Delete memory entries older than the specified number of days."""
        delete_query = f"""
        DELETE FROM {self.table_name}
        WHERE project_name = ?
        AND timestamp < datetime('now', ?);
        """
        time_threshold = f"-{days} days"
        try:
            with self.lock, self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(delete_query, (project_name, time_threshold))
                conn.commit()
            logging.info(f"Deleted entries older than {days} days for project '{project_name}'.")
        except sqlite3.Error as e:
            logging.error(f"Failed to delete old memories for project '{project_name}': {e}")

    def summarize_memories(self, project_name: str, limit: int = 100) -> str:
        """Summarize recent memory entries for a project."""
        memory_summary = self.retrieve_memory(project_name, limit)
        summarized_entries = memory_summary.splitlines()[:limit]
        summary = "\n".join(summarized_entries)
        logging.info(f"Summarized memories for project '{project_name}'.")
        return summary

    def close(self):
        """Close any active database connections (if needed)."""
        logging.debug("MemoryManager close method called. No explicit close operation required with context management.")
