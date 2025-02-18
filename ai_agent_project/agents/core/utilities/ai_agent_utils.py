"""
This Python script contains several classes and methods for performance monitoring and memory management in an AI system.

1. `PerformanceMonitor` class: This is a utility class that helps to track and log the execution performance of an AI system. It provides timing, logging, and optionally, the usage of system resources (CPU and Memory).

2. `MemoryManager` class: This is a utility class that manages the short-term memory of AI agents. It keeps track of the past interactions and task history.

3
"""

import time
import logging
import json
from collections import deque
from typing import Any, Dict, List, Optional, Union, Callable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Optional system usage (CPU & memory) tracking with psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not installed. CPU & memory usage tracking disabled.")

class PerformanceMonitor:
    """
    Tracks and logs execution performance for AI Agents.
    Provides timing, logging, and optional system usage (CPU/mem) insights.
    """

    def __init__(self, max_entries: int = 100, track_system_usage: bool = False):
        """
        Initializes the PerformanceMonitor.

        Args:
            max_entries (int): Maximum number of performance logs to store.
            track_system_usage (bool): If True (and psutil installed), log CPU/mem usage.
        """
        self.execution_logs = deque(maxlen=max_entries)
        self.track_system_usage = track_system_usage

    def track_execution(self, function: Callable) -> Callable:
        """
        Decorator to measure execution time (and optional system usage) of a function.

        Usage:
            @performance_monitor.track_execution
            def my_function(...):
                ...

        Args:
            function (Callable): The function to be wrapped.

        Returns:
            Callable: The wrapped function with performance logging.
        """
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # Optionally track CPU and memory before execution
            cpu_before = psutil.cpu_percent(interval=None) if (PSUTIL_AVAILABLE and self.track_system_usage) else None
            mem_before = psutil.virtual_memory().percent if (PSUTIL_AVAILABLE and self.track_system_usage) else None

            result = function(*args, **kwargs)

            end_time = time.time()

            # Optionally track CPU and memory after execution
            cpu_after = psutil.cpu_percent(interval=None) if (PSUTIL_AVAILABLE and self.track_system_usage) else None
            mem_after = psutil.virtual_memory().percent if (PSUTIL_AVAILABLE and self.track_system_usage) else None

            execution_time = end_time - start_time
            log_entry = {
                "function": function.__name__,
                "execution_time_sec": execution_time,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            if self.track_system_usage and PSUTIL_AVAILABLE:
                log_entry.update({
                    "cpu_before": cpu_before,
                    "cpu_after": cpu_after,
                    "mem_before": mem_before,
                    "mem_after": mem_after
                })

            self.execution_logs.append(log_entry)
            logger.info(f"[PerformanceMonitor] {function.__name__} took {execution_time:.4f}s")

            return result

        return wrapper

    def get_performance_log(self) -> List[Dict[str, Any]]:
        """
        Returns a list of recent performance logs.

        Returns:
            List[Dict[str, Any]]: Execution performance and optional system usage data.
        """
        return list(self.execution_logs)

    def clear_logs(self):
        """
        Clears all stored performance logs.
        """
        self.execution_logs.clear()
        logger.info("Performance logs cleared.")

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

class StructuredMemorySegment:
    """
    A structured memory record that stores text, metadata, tags, or embeddings
    for advanced retrieval or classification.
    """

    def __init__(self, text: str, metadata: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None):
        """
        Initializes a structured memory record.

        Args:
            text (str): The main textual content to store.
            metadata (Optional[Dict[str, Any]]): Additional descriptive data.
            tags (Optional[List[str]]): Tags/labels for classification or search.
        """
        self.text = text
        self.metadata = metadata or {}
        self.tags = tags or []

    def __repr__(self) -> str:
        return f"<StructuredMemorySegment tags={self.tags}, metadata={self.metadata}>"

class VectorMemoryManager(MemoryManager):
    """
    A specialized MemoryManager that stores embeddings for semantic/long-term search.
    (Conceptual example; actual embedding logic requires an NLP library like sentence_transformers.)
    """

    def __init__(self, memory_limit: int = 50, embedding_model: Optional[Any] = None):
        """
        Initializes VectorMemoryManager with optional embedding model.

        Args:
            memory_limit (int): Maximum number of memory entries.
            embedding_model (Optional[Any]): A placeholder for a real embedding model.
        """
        super().__init__(memory_limit=memory_limit)
        self.embedding_model = embedding_model
        self.vector_memory = deque(maxlen=memory_limit)

    def store_segment(self, segment: StructuredMemorySegment) -> None:
        """
        Stores a structured memory segment along with an optional embedding.

        Args:
            segment (StructuredMemorySegment): The memory segment to store.
        """
        embedding = None
        if self.embedding_model:
            # Example: embedding = self._compute_embedding(segment.text)
            # We'll store a dummy value here to avoid real dependencies:
            embedding = [0.0]

        self.vector_memory.append({"segment": segment, "embedding": embedding})
        logger.debug(f"Stored segment: {segment}")

    def search_by_text(self, query_text: str, top_k: int = 3) -> List[StructuredMemorySegment]:
        """
        Conceptual method for semantic search using embeddings.

        Args:
            query_text (str): The query text to embed and compare.
            top_k (int): Number of top matches to return.

        Returns:
            List[StructuredMemorySegment]: Best matching segments (placeholder logic).
        """
        if not self.embedding_model:
            logger.warning("No embedding model provided; returning empty result.")
            return []

        # Example logic to "compute" an embedding:
        # query_embedding = self._compute_embedding(query_text)
        # placeholder approach: return the last few segments
        results = [item["segment"] for item in list(self.vector_memory)[-top_k:]]
        return results

    def _compute_embedding(self, text: str) -> Any:
        """
        Computes text embeddings using the provided model (conceptual).
        """
        if not self.embedding_model:
            return None
        # return self.embedding_model.encode(text)
        # We'll simulate an embedding output:
        return [0.0]

if __name__ == "__main__":
    # Example usage:
    logger.info("Initializing PerformanceMonitor, MemoryManager, and VectorMemoryManager...")

    perf_monitor = PerformanceMonitor(track_system_usage=False)

    @perf_monitor.track_execution
    def sample_task(duration: float):
        time.sleep(duration)
        return f"Slept for {duration} second(s)."

    print(sample_task(1.0))  # demonstrates timing

    mem_manager = MemoryManager(memory_limit=5)
    mem_manager.store_memory("greeting", "Hello, world!")
    print(mem_manager.retrieve_memory("greeting"))

    vec_manager = VectorMemoryManager(embedding_model="dummy_model")
    segment = StructuredMemorySegment("Agent states: Hello!")
    vec_manager.store_segment(segment)
    print(vec_manager.search_by_text("Hello!"))
