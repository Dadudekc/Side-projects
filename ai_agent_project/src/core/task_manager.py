import asyncio
from concurrent.futures import ThreadPoolExecutor
from reasoner_controller import ReasonerController

class TaskManager:
    """
    Manages task execution for the ChainOfThoughtReasoner, including asynchronous processing.
    """

    def __init__(self):
        self.controller = ReasonerController()
        self.executor = ThreadPoolExecutor(max_workers=3)  # Adjust thread pool size as needed

    async def run_task_async(self, task: str) -> str:
        """
        Runs a reasoning task asynchronously.
        
        Args:
            task (str): The task to process.

        Returns:
            str: The result of the task.
        """
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, self.controller.handle_task, task)
        return result

    def run_task_sync(self, task: str) -> str:
        """
        Runs a reasoning task synchronously.
        
        Args:
            task (str): The task to process.

        Returns:
            str: The result of the task.
        """
        return self.controller.handle_task(task)
