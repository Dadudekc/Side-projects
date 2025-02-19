"""

This module provides a series of unit tests for various modules within the ai_agent_utils package, including PerformanceMonitor, MemoryManager, StructuredMemorySegment, and VectorMemoryManager.

These classes are tested:

- TestPerformanceMonitor: Tests for the PerformanceMonitor class, including tracking of execution time and clearing of logs.
- TestMemoryManager: Tests for the MemoryManager class, covering storage and retrieving of memory, clearing memory storage, and exporting and importing memory to and from a file.
- TestStructured
"""

import json
import os
import time
import unittest

from agents.core.utilities.ai_agent_utils import (
    MemoryManager,
    PerformanceMonitor,
    StructuredMemorySegment,
    VectorMemoryManager,
)


class TestPerformanceMonitor(unittest.TestCase):
    """Test suite for PerformanceMonitor."""

    def setUp(self):
        self.monitor = PerformanceMonitor()

    def test_track_execution(self):
        """Test execution time tracking."""

        @self.monitor.track_execution
        def sample_function():
            time.sleep(0.1)
            return "done"

        result = sample_function()
        logs = self.monitor.get_performance_log()

        self.assertEqual(result, "done")
        self.assertGreaterEqual(len(logs), 1)
        self.assertIn("execution_time_sec", logs[0])

    def test_clear_logs(self):
        """Test clearing performance logs."""
        self.monitor.clear_logs()
        self.assertEqual(len(self.monitor.get_performance_log()), 0)


class TestMemoryManager(unittest.TestCase):
    """Test suite for MemoryManager."""

    def setUp(self):
        self.memory_manager = MemoryManager()

    def test_store_and_retrieve_memory(self):
        """Test storing and retrieving memory."""
        self.memory_manager.store_memory("test_key", "test_value")
        retrieved = self.memory_manager.retrieve_memory("test_key")
        self.assertEqual(retrieved, "test_value")

    def test_clear_memory(self):
        """Test clearing memory storage."""
        self.memory_manager.store_memory("key", "value")
        self.memory_manager.clear_memory()
        self.assertIsNone(self.memory_manager.retrieve_memory("key"))

    def test_export_and_import_memory(self):
        """Test exporting and importing memory to/from a file."""
        filepath = "test_memory.json"
        self.memory_manager.store_memory("test_key", "test_value")
        self.memory_manager.export_memory(filepath)

        new_manager = MemoryManager()
        new_manager.import_memory(filepath)
        retrieved = new_manager.retrieve_memory("test_key")

        self.assertEqual(retrieved, "test_value")
        os.remove(filepath)


class TestStructuredMemorySegment(unittest.TestCase):
    """Test suite for StructuredMemorySegment."""

    def test_create_segment(self):
        """Test creating a structured memory segment."""
        segment = StructuredMemorySegment(
            "Test text", {"meta": "data"}, ["tag1", "tag2"]
        )
        self.assertEqual(segment.text, "Test text")
        self.assertEqual(segment.metadata["meta"], "data")
        self.assertIn("tag1", segment.tags)
        self.assertIn("tag2", segment.tags)


class TestVectorMemoryManager(unittest.TestCase):
    """Test suite for VectorMemoryManager."""

    def setUp(self):
        self.vector_manager = VectorMemoryManager()

    def test_store_segment(self):
        """Test storing a segment in vector memory."""
        segment = StructuredMemorySegment("Test segment", {}, [])
        self.vector_manager.store_segment(segment)
        self.assertEqual(len(self.vector_manager.vector_memory), 1)
        self.assertEqual(
            self.vector_manager.vector_memory[0]["segment"].text, "Test segment"
        )

    def test_search_by_text_without_model(self):
        """Test searching stored segments without an AI model."""
        segment1 = StructuredMemorySegment("Text 1", {}, [])
        segment2 = StructuredMemorySegment("Text 2", {}, [])
        self.vector_manager.store_segment(segment1)
        self.vector_manager.store_segment(segment2)

        # Debug: Print stored segments before searching
        print("\nStored Segments:", [seg["segment"].text for seg in self.vector_manager.vector_memory])

        results = self.vector_manager.search_by_text("Text")

        # Debug: Print actual search results
        print("\nSearch Results:", [res.text for res in results])

        # Assertions
        self.assertEqual(len(results), 2, f"Expected 2 results, got {len(results)}")
        self.assertEqual(results[0].text, "Text 1")
        self.assertEqual(results[1].text, "Text 2")



if __name__ == "__main__":
    unittest.main()
