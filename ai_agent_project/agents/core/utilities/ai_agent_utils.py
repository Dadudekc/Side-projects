import time
import logging
import json
from collections import deque
from typing import List, Optional, Any, Dict, Union, Callable

import numpy as np
from sentence_transformers import SentenceTransformer

# Optional system usage (CPU & memory) tracking with psutil.
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.getLogger(__name__).warning("psutil not installed. CPU & memory usage tracking disabled.")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PerformanceMonitor:
    """
    Tracks and logs execution performance for AI Agents.
    Provides timing, logging, and optional system usage (CPU/memory) insights.
    """

    def __init__(self, max_entries: int = 100, track_system_usage: bool = False):
        """
        Initializes the PerformanceMonitor.

        Args:
            max_entries (int): Maximum number of performance logs to store.
            track_system_usage (bool): If True (and psutil is installed), log CPU/memory usage.
        """
        self.execution_logs: deque[Dict[str, Any]] = deque(maxlen=max_entries)
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
            cpu_before = psutil.cpu_percent(interval=None) if (PSUTIL_AVAILABLE and self.track_system_usage) else None
            mem_before = psutil.virtual_memory().percent if (PSUTIL_AVAILABLE and self.track_system_usage) else None

            result = function(*args, **kwargs)
            end_time = time.time()

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

    def clear_logs(self) -> None:
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
        self.memory: deque[Dict[str, Any]] = deque(maxlen=memory_limit)

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
    """

    def __init__(self, memory_limit: int = 50, embedding_model: Optional[str] = "all-MiniLM-L6-v2"):
        """
        Initializes VectorMemoryManager with an optional pre-trained embedding model.

        Args:
            memory_limit (int): Maximum number of memory entries.
            embedding_model (Optional[str]): Pre-trained embedding model from sentence_transformers.
                                             If None, fallback substring search is used.
        """
        super().__init__(memory_limit=memory_limit)
        try:
            self.embedding_model: Optional[SentenceTransformer] = SentenceTransformer(embedding_model) if embedding_model else None
        except Exception as e:
            logger.error(f"Failed to load embedding model '{embedding_model}': {e}")
            self.embedding_model = None
        self.vector_memory: deque[Dict[str, Any]] = deque(maxlen=memory_limit)

    def store_segment(self, segment: StructuredMemorySegment) -> None:
        """
        Stores a structured memory segment along with its embedding.

        Args:
            segment (StructuredMemorySegment): The memory segment to store.
        """
        embedding = self._compute_embedding(segment.text) if self.embedding_model else None
        self.vector_memory.append({"segment": segment, "embedding": embedding})
        logger.debug(f"Stored segment: {segment}")

    def search_by_text(self, query_text: str, top_k: int = 3) -> List[StructuredMemorySegment]:
        """
        Searches for segments matching the query text.

        If an embedding model is provided, a semantic search using cosine similarity is performed.
        Otherwise, falls back to a case-insensitive substring search.

        Args:
            query_text (str): The query text to search for.
            top_k (int): Maximum number of results to return.

        Returns:
            List[StructuredMemorySegment]: List of matching segments.
        """
        if self.embedding_model is None:
            logger.info("No embedding model provided; using fallback substring search.")
            results = [
                item["segment"]
                for item in self.vector_memory
                if query_text.lower() in item["segment"].text.lower()
            ]
            return results[:top_k]
        else:
            query_embedding = self._compute_embedding(query_text)
            scored_segments = [
                (self._cosine_similarity(query_embedding, item["embedding"]), item["segment"])
                for item in self.vector_memory
                if item["embedding"] is not None
            ]
            scored_segments.sort(key=lambda x: x[0], reverse=True)
            return [segment for score, segment in scored_segments][:top_k]

    def _compute_embedding(self, text: str) -> List[float]:
        """
        Computes an embedding for the given text using the pre-trained model.

        Args:
            text (str): The text to embed.

        Returns:
            List[float]: The embedding vector as a list of floats.
        """
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error computing embedding for text '{text}': {e}")
            return []

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """
        Computes cosine similarity between two vectors using NumPy.

        Args:
            v1 (List[float]): First vector.
            v2 (List[float]): Second vector.

        Returns:
            float: Cosine similarity score.
        """
        v1_np = np.array(v1)
        v2_np = np.array(v2)
        norm1 = np.linalg.norm(v1_np)
        norm2 = np.linalg.norm(v2_np)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1_np, v2_np) / (norm1 * norm2))


if __name__ == "__main__":
    # Example usage:
    logger.info("Initializing PerformanceMonitor, MemoryManager, and VectorMemoryManager...")

    perf_monitor = PerformanceMonitor(track_system_usage=False)

    @perf_monitor.track_execution
    def sample_task(duration: float) -> str:
        time.sleep(duration)
        return f"Slept for {duration} second(s)."

    print(sample_task(1.0))  # Demonstrates timing

    mem_manager = MemoryManager(memory_limit=5)
    mem_manager.store_memory("greeting", "Hello, world!")
    print(mem_manager.retrieve_memory("greeting"))

    # Attempt to initialize with a valid model; if model loading fails, fallback will occur.
    vec_manager = VectorMemoryManager(embedding_model="all-MiniLM-L6-v2")
    segment = StructuredMemorySegment("Agent states: Hello!")
    vec_manager.store_segment(segment)
    # Perform a semantic search (or fallback substring search if embedding model unavailable)
    results = vec_manager.search_by_text("Hello!")
    print("Search results:", results)
