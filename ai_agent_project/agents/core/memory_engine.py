"""

A class used to represent the Memory Engine which stores user interactions to enable auto-learning. 

Attributes
----------
memory : dict
    A dictionary storing user queries as well as their corresponding responses. 

Methods
-------
load_memory() -> dict: 
    Loads user interactions from the JSON file if it exists, else it returns an empty list. 

save_memory(): 
    Saves changes made to the memory (user interactions) into the JSON file. 

store_interaction(user_query: str, response:
"""

import json
import os

class MemoryEngine:
    """
    🧠 Stores user interactions to enable auto-learning.
    Uses JSON-based persistent memory for adaptive insights.
    """

    MEMORY_FILE = "data/memory.json"

    def __init__(self):
        self.memory = self.load_memory()

    def load_memory(self) -> dict:
        """Loads stored user interactions from file."""
        if os.path.exists(self.MEMORY_FILE):
            with open(self.MEMORY_FILE, "r") as f:
                return json.load(f)
        return {"conversations": []}

    def save_memory(self):
        """Saves interactions to file."""
        with open(self.MEMORY_FILE, "w") as f:
            json.dump(self.memory, f, indent=4)

    def store_interaction(self, user_query: str, response: str):
        """Stores interactions for future reference."""
        self.memory["conversations"].append({"user": user_query, "response": response})
        self.save_memory()

    def retrieve_similar_query(self, user_query: str) -> str:
        """Finds similar queries and suggests responses."""
        for entry in self.memory["conversations"]:
            if user_query in entry["user"]:
                return entry["response"]
        return None
