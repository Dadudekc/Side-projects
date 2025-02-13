# Path: ai_agent_project/src/core/agent_dispatcher.py

# -------------------------------------------------------------------
# File Path: ai_agent_project/src/core/agent_dispatcher.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# Implements the `AgentDispatcher` class, responsible for dispatching tasks
# to various AI agents, managing task queues, handling errors, rate limiting,
# and integrating memory and performance monitoring. It also defines the
# `AIAgentWithMemory` class, representing an AI agent capable of interacting
# with users, retaining memory, and self-improving based on performance metrics.
#
# Classes:
# - RateLimiter: Custom asynchronous rate limiter using a token bucket algorithm.
# - AgentDispatcher: Manages task dispatching, agent loading, execution, and error handling.
# - AIAgentWithMemory: Represents an AI agent with memory retention and self-improvement capabilities.
#
# Usage:
# Instantiate the `AgentDispatcher` with the directory containing agent plugins.
# Use the `dispatch_task` method to submit tasks to agents.
# Run the dispatcher using the `run` coroutine within an asyncio event loop.
# -------------------------------------------------------------------

import importlib.util
import logging
import os
import sys
import asyncio
from typing import Any, Dict, Optional, Callable, Tuple, List
from pathlib import Path
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Add the project root directory to the system path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utilities.ai_agent_utils import PerformanceMonitor, MemoryManager
from utilities.ChainOfThoughtReasoner import ChainOfThoughtReasoner
from plugins.plugin_interface import AgentPlugin
from db.database import async_session
from db.models import Agent, Task
from sqlalchemy.future import select
from utilities.ai_cache import AICache
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Prevent duplicate handlers
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Metrics using Prometheus Client
from prometheus_client import Counter, Histogram

TASK_SUBMITTED = Counter('tasks_submitted_total', 'Total tasks submitted')
TASK_COMPLETED = Counter('tasks_completed_total', 'Total tasks completed')
TASK_FAILED = Counter('tasks_failed_total', 'Total tasks failed')
TASK_DURATION = Histogram('task_duration_seconds', 'Duration of task execution')
TASK_IN_PROGRESS = Counter('tasks_in_progress', 'Tasks currently in progress')


class RateLimiter:
    """Custom rate limiter using asyncio with a token bucket algorithm."""

    def __init__(self, rate_limit: int, time_window: int):
        """
        Initializes the RateLimiter.

        Args:
            rate_limit (int): Max number of tasks allowed in the time window.
            time_window (int): Time window in seconds for rate limit.
        """
        self.rate_limit = rate_limit
        self.time_window = timedelta(seconds=time_window)
        self.tasks = []

    async def acquire(self):
        """Acquires permission to proceed if under rate limit."""
        now = datetime.utcnow()
        # Remove tasks outside the time window
        self.tasks = [t for t in self.tasks if t > now - self.time_window]

        if len(self.tasks) >= self.rate_limit:
            sleep_duration = (self.tasks[0] + self.time_window - now).total_seconds()
            logger.debug(f"Rate limiter activated. Sleeping for {sleep_duration:.2f} seconds.")
            await asyncio.sleep(sleep_duration)

        self.tasks.append(datetime.utcnow())

    def release(self):
        """Releases a token back to the bucket."""
        if self.tasks:
            self.tasks.pop(0)


class AgentDispatcher:
    """
    Dispatches tasks to agents, supporting chain-of-thought reasoning,
    dynamic agent loading via plugins, and persistent task management.
    """

    def __init__(
        self,
        agents_directory: str,
        model_name: str = "mistral-model",
        ollama_url: str = "http://localhost:11434",
        max_retries: int = 3,
    ):
        """
        Initializes the AgentDispatcher with necessary utilities and dynamically loads agents.

        Args:
            agents_directory (str): The directory where agent plugin modules are located.
            model_name (str): The name of the Mistral model configured in Ollama.
            ollama_url (str): The base URL for the Ollama API.
            max_retries (int): Maximum number of retries for task execution.
        """
        self.memory_manager = MemoryManager()
        self.performance_monitor = PerformanceMonitor()
        self.max_retries = max_retries
        self.agents = self.load_agents(agents_directory)
        self.task_queue: asyncio.PriorityQueue[Tuple[int, str, str, Dict[str, Any]]] = asyncio.PriorityQueue()
        self.dead_letter_queue: asyncio.Queue[Tuple[int, str, str, Dict[str, Any]]] = asyncio.Queue()
        self.chain_of_thought_reasoner = ChainOfThoughtReasoner(
            agent_dispatcher=self,
            model_name=model_name,
            ollama_url=ollama_url,
        )
        self.rate_limiters = {
            agent_name: RateLimiter(10, 60) for agent_name in self.agents.keys()
        }  # Example: 10 tasks per 60 seconds per agent
        self.ai_cache = AICache("ai_cache.json")
        logger.info("AgentDispatcher initialized with dynamically loaded agents.")

    def load_agents(self, agents_directory: str) -> Dict[str, AgentPlugin]:
        """
        Loads agent plugins from the specified directory.

        Args:
            agents_directory (str): Directory containing agent plugin modules.

        Returns:
            Dict[str, AgentPlugin]: Loaded agent instances.
        """
        agents: Dict[str, AgentPlugin] = {}
        agents_path = Path(agents_directory)
        if not agents_path.is_dir():
            logger.error(f"Agents directory '{agents_directory}' does not exist.")
            return agents

        logger.info(f"Loading agent plugins from directory: {agents_directory}")

        for plugin_file in agents_path.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue

            module_name = plugin_file.stem
            try:
                module_spec = importlib.util.spec_from_file_location(
                    module_name, plugin_file
                )
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)

                # Find classes inheriting from AgentPlugin
                for attribute_name in dir(module):
                    attribute = getattr(module, attribute_name)
                    if (
                        isinstance(attribute, type)
                        and issubclass(attribute, AgentPlugin)
                        and attribute is not AgentPlugin
                    ):
                        agent_instance = attribute(
                            name=attribute_name.lower(),
                            memory_manager=self.memory_manager,
                            performance_monitor=self.performance_monitor,
                            dispatcher=self,
                        )
                        agents[agent_instance.name] = agent_instance
                        logger.info(f"Loaded agent plugin: {agent_instance.name}")
            except Exception as e:
                logger.exception(f"Failed to load agent plugin '{module_name}': {e}")

        logger.info(f"Total agents loaded: {len(agents)} - {list(agents.keys())}")
        return agents

    async def dispatch_task(
        self,
        task: str,
        agent_name: str,
        priority: int = 1,
        use_chain_of_thought: bool = False,
        **kwargs
    ) -> Optional[Any]:
        """
        Dispatches a task to an agent, with optional Chain-of-Thought reasoning.

        Args:
            task (str): Task description.
            agent_name (str): Target agent name.
            priority (int): Task priority; lower numbers are higher priority.
            use_chain_of_thought (bool): Whether to use CoT reasoning.
            **kwargs: Additional arguments for the agent.

        Returns:
            Optional[Any]: Task result if CoT is used, else None.
        """
        logger.debug(
            f"Dispatching task '{task}' to agent '{agent_name}' with priority '{priority}'."
        )

        agent = self.agents.get(agent_name)
        if not agent:
            error_message = f"Agent '{agent_name}' not found."
            logger.error(error_message)
            TASK_FAILED.inc()
            return error_message

        # Persist task to the database
        async with async_session() as session:
            try:
                stmt = select(Agent).where(Agent.name == agent_name)
                result = await session.execute(stmt)
                agent_record = result.scalars().first()
                if not agent_record:
                    # Create agent record if it doesn't exist
                    agent_record = Agent(name=agent_name)
                    session.add(agent_record)
                    await session.commit()
                    logger.info(f"Agent '{agent_name}' added to database with ID {agent_record.id}.")

                new_task = Task(
                    description=task,
                    agent_id=agent_record.id,
                    priority=priority,
                    use_chain_of_thought=use_chain_of_thought,
                    status="queued",
                    created_at=datetime.utcnow(),
                )
                session.add(new_task)
                await session.commit()
                logger.info(
                    f"Task '{task}' persisted to database with ID {new_task.id}."
                )
                TASK_SUBMITTED.inc()
            except SQLAlchemyError as e:
                logger.exception(f"Database error while persisting task '{task}': {e}")
                TASK_FAILED.inc()
                return f"Database error: {e}"

        if use_chain_of_thought:
            return await self._execute_with_chain_of_thought(task, agent_name)
        else:
            # Enqueue the task
            await self.task_queue.put((priority, task, agent_name, kwargs))
            logger.info(
                f"Task '{task}' enqueued for agent '{agent_name}' with priority '{priority}'."
            )
            return None

    async def _execute_with_chain_of_thought(
        self, task: str, agent_name: str
    ) -> Optional[str]:
        """
        Executes a task using Chain-of-Thought reasoning.

        Args:
            task (str): Task description.
            agent_name (str): Target agent name.

        Returns:
            Optional[str]: Result from CoT reasoning.
        """
        logger.info(
            f"Executing task '{task}' with Chain-of-Thought for agent '{agent_name}'."
        )
        TASK_IN_PROGRESS.inc()
        start_time = time.time()

        try:
            result = await self.chain_of_thought_reasoner.solve_task_with_reasoning(
                task, agent_name
            )
            logger.info(f"CoT task '{task}' completed with result: {result}")
            await self._update_task_status(task, agent_name, "completed", result)
            TASK_COMPLETED.inc()
            return result
        except Exception as e:
            error_message = f"Error during CoT reasoning for task '{task}': {str(e)}"
            logger.exception(error_message)
            await self._update_task_status(task, agent_name, "failed", error_message)
            TASK_FAILED.inc()
            return error_message
        finally:
            duration = time.time() - start_time
            TASK_DURATION.observe(duration)
            TASK_IN_PROGRESS.dec()
            logger.debug(f"CoT task '{task}' duration: {duration} seconds.")

    async def _execute_standard_task(
        self,
        priority: int,
        task: str,
        agent_name: str,
        kwargs: Dict[str, Any],
        retry_count: int = 0,
    ) -> Optional[str]:
        """
        Executes a standard task asynchronously with retry logic and rate limiting.

        Args:
            priority (int): Task priority.
            task (str): Task description.
            agent_name (str): Target agent name.
            kwargs (Dict[str, Any]): Additional arguments for the agent.
            retry_count (int): Current retry attempt.

        Returns:
            Optional[str]: Result from the task execution.
        """
        agent = self.agents.get(agent_name)
        if not agent:
            error_message = f"Agent '{agent_name}' not found."
            logger.error(error_message)
            TASK_FAILED.inc()
            return error_message

        rate_limiter = self.rate_limiters.get(agent_name)
        if rate_limiter:
            await rate_limiter.acquire()
            logger.debug(f"Rate limiter acquired for agent '{agent_name}'.")

        TASK_IN_PROGRESS.inc()
        start_time = time.time()

        try:
            # Update task status to running
            await self._update_task_status(task, agent_name, "running", None)

            # Execute the agent's task asynchronously
            result = await agent.solve_task(task, **kwargs)
            self.performance_monitor.log_performance(agent_name, task, result)

            logger.info(
                f"Task '{task}' executed by agent '{agent_name}' with result: {result}"
            )

            # Update task status to completed
            await self._update_task_status(task, agent_name, "completed", result)
            TASK_COMPLETED.inc()
            return result
        except Exception as e:
            logger.exception(
                f"Error executing task '{task}' for agent '{agent_name}': {e}"
            )
            if retry_count < self.max_retries:
                backoff = 2 ** retry_count
                logger.info(
                    f"Retrying task '{task}' for agent '{agent_name}' in {backoff} seconds (Attempt {retry_count + 1}/{self.max_retries})"
                )
                await asyncio.sleep(backoff)
                return await self._execute_standard_task(
                    priority, task, agent_name, kwargs, retry_count + 1
                )
            else:
                error_message = f"Task '{task}' for agent '{agent_name}' failed after {self.max_retries} attempts."
                logger.error(error_message)
                await self.dead_letter_queue.put((priority, task, agent_name, kwargs))
                self._send_alert(error_message)
                await self._update_task_status(task, agent_name, "failed", str(e))
                TASK_FAILED.inc()
                return f"Error executing task: {e}"
        finally:
            duration = time.time() - start_time
            TASK_DURATION.observe(duration)
            TASK_IN_PROGRESS.dec()
            logger.debug(f"Task '{task}' duration: {duration} seconds.")
            if rate_limiter:
                rate_limiter.release()
                logger.debug(f"Rate limiter released for agent '{agent_name}'.")

    async def execute_tasks(self):
        """
        Executes tasks from the priority queue asynchronously.
        """
        logger.info("Starting task execution loop.")
        while True:
            if not self.task_queue.empty():
                priority, task, agent_name, kwargs = await self.task_queue.get()
                logger.debug(
                    f"Dequeuing task '{task}' for agent '{agent_name}' with priority '{priority}'."
                )
                asyncio.create_task(
                    self._execute_standard_task(priority, task, agent_name, kwargs)
                )
            else:
                await asyncio.sleep(1)  # Adjust sleep time as needed

    async def run(self):
        """
        Starts the dispatcher and begins processing tasks.
        """
        logger.info("AgentDispatcher is running.")
        await asyncio.gather(
            self.execute_tasks(),
            self.monitor_dead_letter_queue(),
        )

    async def monitor_dead_letter_queue(self):
        """
        Monitors the dead-letter queue for failed tasks.
        """
        while True:
            if not self.dead_letter_queue.empty():
                priority, task, agent_name, kwargs = await self.dead_letter_queue.get()
                logger.warning(
                    f"Dead-letter task '{task}' for agent '{agent_name}' detected. Manual intervention required."
                )
                # Implement alerting or logging mechanisms here
                self._send_alert(
                    f"Dead-letter task '{task}' for agent '{agent_name}' requires attention."
                )
            else:
                await asyncio.sleep(5)  # Adjust sleep time as needed

    def add_agent(self, agent_instance: AgentPlugin):
        """
        Adds a new agent to the dispatcher dynamically.

        Args:
            agent_instance (AgentPlugin): The agent instance to add.
        """
        self.agents[agent_instance.name] = agent_instance
        self.rate_limiters[agent_instance.name] = RateLimiter(10, 60)  # Example rate limit
        logger.info(f"Added agent '{agent_instance.name}' dynamically.")

    def remove_agent(self, agent_name: str):
        """
        Removes an agent from the dispatcher.

        Args:
            agent_name (str): The name of the agent to remove.
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            del self.rate_limiters[agent_name]
            logger.info(f"Removed agent '{agent_name}' from dispatcher.")
        else:
            logger.warning(f"Attempted to remove non-existent agent '{agent_name}'.")

    def list_agents(self) -> List[str]:
        """
        Lists all registered agents.

        Returns:
            List[str]: Names of all agents currently available.
        """
        agent_names = list(self.agents.keys())
        logger.info("Registered agents:")
        for name in agent_names:
            capabilities = (
                self.agents[name].describe_capabilities()
                if hasattr(self.agents[name], "describe_capabilities")
                else "No description available."
            )
            logger.info(f" - {name}: {capabilities}")
        return agent_names

    async def _update_task_status(
        self, task: str, agent_name: str, status: str, result: Optional[str]
    ):
        """
        Updates the status and result of a task in the database.

        Args:
            task (str): Task description.
            agent_name (str): Target agent name.
            status (str): New status ('completed', 'failed', etc.).
            result (Optional[str]): Result or error message.
        """
        async with async_session() as session:
            try:
                stmt = select(Agent).where(Agent.name == agent_name)
                result_agent = await session.execute(stmt)
                agent_record = result_agent.scalars().first()

                if not agent_record:
                    logger.error(
                        f"Agent '{agent_name}' not found in database while updating task '{task}'."
                    )
                    return

                stmt = select(Task).where(
                    Task.description == task,
                    Task.agent_id == agent_record.id,
                    Task.status.in_(["running", "queued"]),
                ).order_by(Task.created_at.desc())
                result_task = await session.execute(stmt)
                task_record = result_task.scalars().first()

                if task_record:
                    task_record.status = status
                    task_record.result = result
                    task_record.updated_at = datetime.utcnow()
                    await session.commit()
                    logger.info(
                        f"Task '{task}' for agent '{agent_name}' updated to status '{status}'."
                    )
                else:
                    logger.error(
                        f"No matching task found in database for task '{task}' and agent '{agent_name}'."
                    )
            except SQLAlchemyError as e:
                logger.exception(f"Database error while updating task '{task}': {e}")

    def _send_alert(self, message: str):
        """
        Sends an alert for critical failures.

        Args:
            message (str): Alert message.
        """
        # Implement alerting mechanisms (e.g., email, Slack)
        logger.error(f"ALERT: {message}")


class AIAgentWithMemory(AgentPlugin):
    """
    AIAgentWithMemory Class

    Represents an AI agent that can interact with users, retain memory of past
    conversations, provide context-aware responses, and improve itself based on feedback.
    Integrates with the MemoryManager and PerformanceMonitor to handle memory and performance operations.
    """

    def __init__(
        self,
        name: str,
        project_name: str,
        memory_manager: MemoryManager,
        performance_monitor: PerformanceMonitor,
        dispatcher: Optional[AgentDispatcher] = None,
    ):
        """
        Initialize the AI agent with a name, project name, a MemoryManager instance,
        and a PerformanceMonitor instance.

        Args:
            name (str): Name of the AI agent.
            project_name (str): Name of the project/domain the agent is associated with.
            memory_manager (MemoryManager): Instance of MemoryManager for handling memory operations.
            performance_monitor (PerformanceMonitor): Instance of PerformanceMonitor for tracking performance.
            dispatcher (AgentDispatcher): Reference to the dispatcher for self-improvement actions.
        """
        super().__init__(name=name)
        if dispatcher is None:
            dispatcher = AgentDispatcher(agents_directory="plugins")  # Adjust as needed

        self.project_name = project_name
        self.memory_manager = memory_manager
        self.performance_monitor = performance_monitor
        self.dispatcher = dispatcher
        logger.info(f"Initialized AI Agent '{self.name}' for project '{self.project_name}'.")

    async def solve_task(self, task: str, **kwargs) -> str:
        """
        Solves a given task by interacting with the AI model via Ollama and managing memory.

        Args:
            task (str): Task description.
            **kwargs: Additional keyword arguments.

        Returns:
            str: Response from the AI model or an error message.
        """
        try:
            # Retrieve relevant memory context
            memory_context = self.memory_manager.retrieve_memory(self.project_name, limit=5)
            complete_prompt = f"{memory_context}User: {task}\nAI:"

            logger.debug(f"Complete prompt sent to AI:\n{complete_prompt}")

            # Run the Ollama command with the complete prompt
            process = await asyncio.create_subprocess_exec(
                "ollama", "run", "mistral:latest", "--prompt", complete_prompt,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_message = stderr.decode().strip() or "Unknown error occurred."
                logger.error(f"Error from Ollama: {error_message}")
                self.performance_monitor.log_performance(
                    self.name, task, success=False, response=error_message
                )
                return f"An error occurred: {error_message}"

            response = stdout.decode().strip()
            logger.info(f"Received response from AI for task '{task}': {response}")

            # Save the interaction to memory
            self.memory_manager.save_memory(self.project_name, task, response)

            # Log performance as success
            self.performance_monitor.log_performance(
                self.name, task, success=True, response=response
            )

            return response
        except Exception as ex:
            error_message = f"An unexpected error occurred: {str(ex)}"
            logger.error(error_message)
            self.performance_monitor.log_performance(
                self.name, task, success=False, response=error_message
            )
            return error_message

    def describe_capabilities(self) -> str:
        """
        Returns a description of the agent's capabilities.

        Returns:
            str: Capabilities description.
        """
        capabilities_description = (
            f"{self.name} can interact with users, retain memory of past conversations, "
            f"provide context-aware responses, and self-improve based on performance metrics."
        )
        logger.info("Capabilities described.")
        return capabilities_description

    def self_improve(self):
        """
        Analyze performance and adjust operations to improve future interactions.
        This method embodies the self-improvement capability of the AI agent.
        """
        analysis = self.performance_monitor.analyze_performance(self.name)
        if not analysis:
            logger.info("No performance data available for self-improvement.")
            return

        success_rate = analysis.get('success_rate', 0)
        failures = analysis.get('failures', 0)

        logger.debug(f"Self-improvement analysis: {analysis}")

        # Thresholds for triggering improvements
        SUCCESS_THRESHOLD = 80  # percent
        FAILURE_THRESHOLD = 20  # percent

        if success_rate < SUCCESS_THRESHOLD and failures > FAILURE_THRESHOLD:
            # Identify common failure reasons
            failure_reasons = analysis.get('failure_details', [])
            common_reasons = {}
            for reason in failure_reasons:
                common_reasons[reason] = common_reasons.get(reason, 0) + 1
            # Find the most common failure reason
            if common_reasons:
                most_common_reason = max(common_reasons, key=common_reasons.get)
                logger.warning(f"Most common failure reason: {most_common_reason}")
                # Take action based on failure reason
                self.take_action_based_on_failure(most_common_reason)
        elif success_rate >= SUCCESS_THRESHOLD:
            logger.info("Performance is satisfactory. No immediate improvements needed.")
        else:
            logger.info("Performance analysis does not require immediate action.")

    def take_action_based_on_failure(self, reason: str):
        """
        Takes specific actions based on the identified failure reason.

        Args:
            reason (str): The most common failure reason.
        """
        logger.info(f"Taking action based on failure reason: {reason}")
        # Example actions based on failure reasons
        suggestions = {
            "communication": "I recommend checking the network connection or restarting the AI model service.",
            "permission": "It seems there are permission issues. Please verify the file permissions.",
            "docker": "Docker-related errors detected. Please ensure Docker is properly installed and configured.",
            "timeout": "Increase the AI response timeout threshold or optimize the query for faster processing.",
            # Add more reasons and suggestions as needed
        }

        # Find a suggestion based on the reason
        suggestion = next((msg for key, msg in suggestions.items() if key in reason.lower()),
                          "I encountered an issue that needs attention. Please review the logs for more details.")
        logger.info(suggestion)
        print(f"AI Suggestion: {suggestion}")

    def suggest_improvements(self):
        """
        Suggests improvements to its own operations based on performance data.
        """
        analysis = self.performance_monitor.analyze_performance(self.name)
        if not analysis:
            logger.info("No performance data available to suggest improvements.")
            return

        suggestions = []
        success_rate = analysis.get('success_rate', 0)
        failures = analysis.get('failures', 0)

        if success_rate < 90:
            suggestions.append("Consider refining task division strategies to better handle complex tasks.")
        if failures > 5:
            suggestions.append("Evaluate and possibly upgrade the tools in ToolServer to handle current task demands.")

        if suggestions:
            suggestion_message = "Here are some suggestions to improve my performance:\n" + "\n".join(suggestions)
            logger.info(suggestion_message)
            print(f"AI Suggestion: {suggestion_message}")
        else:
            logger.info("No improvements needed based on current performance data.")


# Example usage:
# if __name__ == "__main__":
#     dispatcher = AgentDispatcher(agents_directory="plugins")
#     asyncio.run(dispatcher.run())
