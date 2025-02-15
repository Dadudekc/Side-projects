import unittest
import time
import json
import os
from agents.core.utilities.ai_agent_utils import (
    PerformanceMonitor,
    MemoryManager,
    StructuredMemorySegment,
    VectorMemoryManager,
)


class TestPerformanceMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = PerformanceMonitor()

    def test_track_execution(self):
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
        self.monitor.clear_logs()
        self.assertEqual(len(self.monitor.get_performance_log()), 0)


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.memory_manager = MemoryManager()

    def test_store_and_retrieve_memory(self):
        self.memory_manager.store_memory("test_key", "test_value")
        retrieved = self.memory_manager.retrieve_memory("test_key")
        self.assertEqual(retrieved, "test_value")

    def test_clear_memory(self):
        self.memory_manager.store_memory("key", "value")
        self.memory_manager.clear_memory()
        self.assertIsNone(self.memory_manager.retrieve_memory("key"))

    def test_export_and_import_memory(self):
        filepath = "test_memory.json"
        self.memory_manager.store_memory("test_key", "test_value")
        self.memory_manager.export_memory(filepath)

        new_manager = MemoryManager()
        new_manager.import_memory(filepath)
        retrieved = new_manager.retrieve_memory("test_key")

        self.assertEqual(retrieved, "test_value")
        os.remove(filepath)


class TestStructuredMemorySegment(unittest.TestCase):
    def test_create_segment(self):
        segment = StructuredMemorySegment(
            "Test text", {"meta": "data"}, ["tag1", "tag2"]
        )
        self.assertEqual(segment.text, "Test text")
        self.assertEqual(segment.metadata["meta"], "data")
        self.assertIn("tag1", segment.tags)
        self.assertIn("tag2", segment.tags)


class TestVectorMemoryManager(unittest.TestCase):
    def setUp(self):
        self.vector_manager = VectorMemoryManager()

    def test_store_segment(self):
        segment = StructuredMemorySegment("Test segment")
        self.vector_manager.store_segment(segment)
        self.assertEqual(len(self.vector_manager.vector_memory), 1)
        self.assertEqual(
            self.vector_manager.vector_memory[0]["segment"].text, "Test segment"
        )

    def test_search_by_text_without_model(self):
        segment1 = StructuredMemorySegment("Text 1")
        segment2 = StructuredMemorySegment("Text 2")
        self.vector_manager.store_segment(segment1)
        self.vector_manager.store_segment(segment2)
        results = self.vector_manager.search_by_text("Test")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].text, "Text 1")
        self.assertEqual(results[1].text, "Text 2")


if __name__ == "__main__":
    unittest.main()
