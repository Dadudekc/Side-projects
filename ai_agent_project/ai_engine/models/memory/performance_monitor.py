import time
import logging
import psutil
from collections import deque
from typing import Any, Dict, List, Callable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

try:
    # If psutil isn't installed, the code won't crash
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
