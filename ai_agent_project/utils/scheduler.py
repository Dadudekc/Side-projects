import time
import threading
import logging

logger = logging.getLogger(__name__)

class TaskScheduler:
    """
    Manages scheduled tasks such as auto-updating trade strategies.
    """

    def __init__(self):
        self.jobs = []

    def schedule_task(self, func, interval: int):
        """
        Schedules a function to run at a set interval.

        Args:
            func (function): The function to execute.
            interval (int): Time in minutes.
        """
        def job():
            while True:
                logger.info("Running scheduled task...")
                func()
                time.sleep(interval * 60)

        thread = threading.Thread(target=job, daemon=True)
        thread.start()
        self.jobs.append(thread)
