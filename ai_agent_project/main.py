import logging
from memory import (
    PerformanceMonitor,
    MemoryManager,
    StructuredMemorySegment,
    VectorMemoryManager
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

performance_monitor = PerformanceMonitor(track_system_usage=False)

@performance_monitor.track_execution
def sample_task(duration: float):
    import time
    time.sleep(duration)
    return f"Slept for {duration} second(s)"

def main():
    print(sample_task(1.0))  # demonstrates timing

    mem_manager = MemoryManager(memory_limit=5)
    mem_manager.store_memory("greeting", "Hello, world!")
    print(mem_manager.retrieve_memory("greeting"))

    vec_manager = VectorMemoryManager(embedding_model="dummy_model")
    segment = StructuredMemorySegment("Agent states: Hello!", {"author": "System"}, ["example"])
    vec_manager.store_segment(segment)
    print(vec_manager.search_by_text("Hello!"))

if __name__ == "__main__":
    main()
