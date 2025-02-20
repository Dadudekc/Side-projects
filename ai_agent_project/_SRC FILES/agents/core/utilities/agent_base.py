# agent_base.py

# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\ai_agent_project\src\agents\core\utilities\agent_base.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# Defines the `RobustAgent` class, which serves as a versatile
# foundational layer for agents within the project. This class provides
# essential functionalities including task scheduling, structured logging,
# dynamic error handling, persistent task state tracking, automated
# retry mechanisms, modular plug-and-play task expansion, AI-driven
# self-healing capabilities, memory management, performance monitoring,
# and user interaction for high-level decisions.
#
# Classes:
# - RobustAgent: A comprehensive agent class that integrates task scheduling,
#   error handling, memory management, performance monitoring, self-improvement,
#   and plugin support.
#
# Usage:
# Agents inheriting from `RobustAgent` should implement the `solve_task` method,
# defining their unique task-solving logic. The base class handles logging,
# scheduling, persistent state management, dynamic plugin loading, AI-driven
# error handling, memory management, performance monitoring, and user interaction
# to ensure task reliability, scalability, and consistency.
# -------------------------------------------------------------------

import asyncio
import abc
import logging
import importlib.util
import json
import os
from typing import Any, Callable, Optional, Dict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
import traceback
import subprocess
from sqlalchemy import create_engine, Column, Integer, String, Enum as SqlEnum, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import enum
import time
from datetime import datetime, timezone, timedelta
from difflib import SequenceMatcher
from memory_manager import MemoryManager
from ChainOfThoughtReasoner import ChainOfThoughtReasoner  # Adjust the import path accordingly

# Database Model Setup
Base = declarative_base()

class TaskState(enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    retrying = "retrying"

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    status = Column(SqlEnum(TaskState), default=TaskState.pending)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime)
    result = Column(Text)  # Text to allow for larger outputs
    retry_count = Column(Integer, default=0)

class ResolutionHistory(Base):
    __tablename__ = 'resolution_history'
    id = Column(Integer, primary_key=True)
    error_message = Column(Text, nullable=False)
    ai_suggestion = Column(Text)
    user_decision = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class UserDecisionCache(Base):
    __tablename__ = 'user_decision_cache'
    id = Column(Integer, primary_key=True)
    error_message = Column(Text, nullable=False, unique=True)
    user_decision = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    usage_count = Column(Integer, default=0)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Database Connection
engine = create_engine('sqlite:///tasks.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class RobustAgent(metaclass=abc.ABCMeta):
    """
    RobustAgent Class

    Represents a comprehensive AI agent with task management, error handling,
    memory management, performance monitoring, and self-improvement capabilities.
    Integrates with MemoryManager, PerformanceMonitor, and ChainOfThoughtReasoner to handle
    memory, performance, and advanced reasoning operations.
    """

    MAX_RETRIES = 3  # Max retries for task failure
    SIMILARITY_THRESHOLD = 0.75  # Threshold for error similarity

    def __init__(self, name: str, description: str, project_name: str, plugin_dir: str = "plugins",
                 memory_manager: Optional[MemoryManager] = None, performance_monitor: Any = None,
                 log_to_file: bool = False, dispatcher=None,
                 reasoner: Optional[ChainOfThoughtReasoner] = None):
        """
        Initialize the RobustAgent with necessary components.

        Args:
            name (str): Name of the AI agent.
            description (str): Description of the agent's capabilities.
            project_name (str): Name of the project/domain the agent is associated with.
            plugin_dir (str): Directory for dynamically loaded task plugins.
            memory_manager (MemoryManager): Instance of MemoryManager for handling memory operations.
            performance_monitor (Any): Instance of PerformanceMonitor for tracking performance.
            log_to_file (bool): Whether to log to a file instead of the console.
            dispatcher (Any): Reference to the dispatcher for self-improvement actions.
            reasoner (ChainOfThoughtReasoner): Instance of ChainOfThoughtReasoner for advanced reasoning.
        """
        self.name = name
        self.description = description
        self.project_name = project_name
        self.plugin_dir = plugin_dir
        self.memory_manager = memory_manager  # Should be an instance of MemoryManager
        self.performance_monitor = performance_monitor  # Should be an instance of PerformanceMonitor
        self.dispatcher = dispatcher
        self.reasoner = reasoner  # Initialize the reasoner

        self.logger = logging.getLogger(self.name)
        self._setup_logger(log_to_file)

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        self.plugins = self.load_plugins()

        self.logger.info(f"Initialized RobustAgent '{self.name}' for project '{self.project_name}'.")

    def _setup_logger(self, log_to_file: bool):
        """Sets up the logging configuration for the agent."""
        if not self.logger.hasHandlers():
            handler = logging.StreamHandler() if not log_to_file else logging.FileHandler(f"{self.name}.log")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log(self, message: str, level=logging.INFO):
        """Logs a message at the specified logging level."""
        self.logger.log(level, message)

    def log_json(self, message: str, data: dict, level=logging.INFO):
        """Logs a structured message with additional data in JSON format."""
        log_entry = {
            "message": message,
            "data": data
        }
        self.logger.log(level, json.dumps(log_entry))

    def log_error(self, error: Exception, context: Optional[dict] = None):
        """Logs an error message with traceback and optional contextual information."""
        error_details = {
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        self.log_json("Error encountered", error_details, level=logging.ERROR)

    def load_plugins(self) -> Dict[str, Callable]:
        """
        Dynamically loads plugins (task handlers) from the specified directory.

        Returns:
            Dict[str, Callable]: A dictionary of plugin functions.
        """
        plugins = {}
        plugin_path = Path(self.plugin_dir)
        if not plugin_path.exists():
            self.logger.warning(f"Plugin directory '{self.plugin_dir}' does not exist. Creating it.")
            plugin_path.mkdir(parents=True, exist_ok=True)
            return plugins

        for plugin_file in plugin_path.glob("*.py"):
            module_name = plugin_file.stem
            try:
                module_spec = importlib.util.spec_from_file_location(module_name, plugin_file)
                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)
                plugin_func = getattr(module, "run_task", None)
                if callable(plugin_func):
                    plugins[module_name] = plugin_func
                    self.logger.info(f"Loaded plugin: {module_name}")
            except Exception as e:
                self.logger.error(f"Error loading plugin '{module_name}': {e}")

        return plugins

    def execute_plugin_task(self, task_name: str, task_data: dict) -> str:
        """
        Executes a task using a dynamically loaded plugin.

        Args:
            task_name (str): The name of the task/plugin to execute.
            task_data (dict): Data to pass to the plugin.

        Returns:
            str: The result of the plugin task or an error message.
        """
        plugin = self.plugins.get(task_name)
        if plugin:
            try:
                self.logger.info(f"Executing plugin task '{task_name}' with data: {task_data}")
                return plugin(task_data)
            except Exception as e:
                self.log_error(e, {"task_name": task_name})
                return f"Error executing plugin '{task_name}': {str(e)}"
        else:
            error_message = f"Plugin '{task_name}' not found."
            self.logger.error(error_message)
            return error_message

    def ai_diagnose_and_resolve(self, error_message: str) -> Optional[str]:
        """
        Uses Mistral through Ollama CLI to diagnose and suggest resolutions for errors.

        Args:
            error_message (str): The error message to diagnose.

        Returns:
            Optional[str]: Suggested resolution from AI, if available.
        """
        prompt = f"Provide a solution for the following error:\n{error_message}"
        try:
            self.logger.info(f"Sending prompt to AI for error diagnosis: {prompt}")
            result = subprocess.run(
                ["ollama", "generate", "--model", "mistral", prompt],
                capture_output=True,
                text=True,
                check=True
            )
            suggestion = result.stdout.strip()
            self.logger.info(f"AI Suggestion for error '{error_message}': {suggestion}")
            return suggestion
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get AI suggestion for error: {error_message}. Error: {e}")
            return None

    def handle_task_with_error_handling(self, task_data: dict, fallback: Optional[Callable] = None) -> str:
        """
        Executes a task with error handling, AI-based resolution, and optional user prompt for oversight.

        Args:
            task_data (dict): Data necessary for task execution.
            fallback (Optional[Callable]): Optional fallback function.

        Returns:
            str: Outcome of the task or error message.
        """
        task_id = self.save_task_state("task_execution", TaskState.pending)
        try:
            # Check if task is complex and requires reasoning
            if task_data.get("type") == "complex_task":
                # Use asynchronous reasoning
                result = asyncio.run(self.solve_task_with_reasoning(task_data.get("description", "")))
            else:
                result = self._execute_with_retry(task_id, task_data)
            self.update_task_state(task_id, TaskState.completed, result=result)
            return result
        except Exception as e:
            self.log_error(e, {"task_data": task_data})
            self.update_task_state(task_id, TaskState.failed)
            return self.handle_error_resolution(task_id, e, fallback)

    def handle_error_resolution(self, task_id: int, error: Exception, fallback: Optional[Callable] = None) -> str:
        """
        Manages the resolution process for errors, including checking history, AI diagnosis,
        cached decisions, and user prompts.

        Args:
            task_id (int): The ID of the failed task.
            error (Exception): The raised exception during task execution.
            fallback (Optional[Callable]): Optional fallback function.

        Returns:
            str: Suggested resolution or fallback message.
        """
        stack_trace = traceback.format_exc()
        error_messages = self._extract_error_messages(stack_trace)

        # Check for existing resolutions
        resolution = self.check_resolution_history(error_messages)
        if resolution:
            self.logger.info(f"Found existing resolution: {resolution.ai_suggestion}")
            return resolution.ai_suggestion

        # Attempt AI-based resolution
        for error_message in error_messages:
            ai_suggestion = self.ai_diagnose_and_resolve(error_message)
            if ai_suggestion:
                self.save_resolution_history(error_message, ai_suggestion)
                return ai_suggestion

        # Check for cached user decision
        user_decision = self.get_cached_user_decision(error_messages)
        if user_decision:
            self.logger.info(f"Applying cached user decision: {user_decision}")
            return user_decision

        # Prompt user for manual resolution
        return self.prompt_user_for_manual_resolution(error_messages, fallback)

    def prompt_user_for_manual_resolution(self, error_messages: list, fallback: Optional[Callable] = None) -> str:
        """
        Prompts the user for a manual resolution when automated methods fail.

        Args:
            error_messages (list): List of error messages to provide context.
            fallback (Optional[Callable]): Optional fallback function.

        Returns:
            str: User-provided manual resolution or fallback message.
        """
        error_context = " | ".join(error_messages)
        user_decision_input = input(f"AI could not resolve the issue: {error_context}. Do you want to attempt manual resolution? (y/n): ")

        if user_decision_input.lower() == 'y':
            manual_resolution = input("Please provide a manual resolution: ")
            self.save_resolution_history(error_context, user_decision=manual_resolution)
            self.cache_user_decision(error_context, manual_resolution)
            return manual_resolution

        # Fallback mechanism
        return fallback() if fallback else "An error occurred while processing the task."

    def _extract_error_messages(self, stack_trace: str) -> list:
        """
        Extracts individual error messages from a stack trace.

        Args:
            stack_trace (str): The full stack trace.

        Returns:
            list: A list of error messages.
        """
        error_messages = []
        for line in stack_trace.splitlines():
            if line.startswith("raise") or "Exception" in line:
                error_messages.append(line.strip())
        return error_messages

    def _execute_with_retry(self, task_id: int, task_data: dict) -> str:
        """
        Executes a task with retry logic, using exponential backoff.
        Retries up to `MAX_RETRIES` if exceptions are raised.

        Args:
            task_id (int): The ID of the task in the database.
            task_data (dict): Data necessary for task execution.

        Returns:
            str: The result of the task.

        Raises:
            Exception: Re-raises the last exception if all retries fail.
        """
        attempt = 0
        while attempt < self.MAX_RETRIES:
            try:
                self.update_task_state(task_id, TaskState.running)
                result = self.solve_task(task_data)
                self.logger.info("Task executed successfully.")
                return result
            except Exception as e:
                attempt += 1
                self.log_error(e, {"attempt": attempt})
                if attempt < self.MAX_RETRIES:
                    self.update_task_state(task_id, TaskState.retrying)
                    backoff = 2 ** attempt
                    self.logger.info(f"Retrying task in {backoff} seconds (Attempt {attempt}/{self.MAX_RETRIES})")
                    time.sleep(backoff)
                else:
                    self.logger.error(f"Max retries reached for task ID {task_id}.")
                    raise

    def save_task_state(self, task_type: str, initial_status: TaskState) -> int:
        """Saves a new task state to the database for fault tolerance."""
        session = Session()
        try:
            task = Task(type=task_type, status=initial_status)
            session.add(task)
            session.commit()
            self.logger.info(f"Task '{task_type}' saved with state '{initial_status.name}' and ID {task.id}.")
            return task.id
        except Exception as e:
            self.logger.error(f"Error saving task state: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def update_task_state(self, task_id: int, new_status: TaskState, result: Optional[str] = None):
        """Updates the status and result of a task in the database."""
        session = Session()
        try:
            task = session.query(Task).filter(Task.id == task_id).one_or_none()
            if task:
                task.status = new_status
                if result:
                    task.result = result
                task.end_time = datetime.now(timezone.utc)
                session.commit()
                self.logger.info(f"Task ID {task_id} updated to status '{new_status.name}' with result: {result}")
            else:
                self.logger.error(f"Task ID {task_id} not found in the database.")
        except Exception as e:
            self.logger.error(f"Error updating task state: {e}")
            session.rollback()
        finally:
            session.close()

    def save_resolution_history(self, error_message: str, ai_suggestion: Optional[str] = None, user_decision: Optional[str] = None):
        """Saves a resolution history entry to the database."""
        session = Session()
        try:
            resolution = ResolutionHistory(
                error_message=error_message,
                ai_suggestion=ai_suggestion,
                user_decision=user_decision
            )
            session.add(resolution)
            session.commit()
            self.logger.info(f"Resolution history saved for error: {error_message}")
        except Exception as e:
            self.logger.error(f"Error saving resolution history: {e}")
            session.rollback()
        finally:
            session.close()

    def check_resolution_history(self, error_messages: list) -> Optional[ResolutionHistory]:
        """
        Checks if there is a resolution history for the given error messages.

        Args:
            error_messages (list): List of error messages.

        Returns:
            Optional[ResolutionHistory]: The resolution history entry if found.
        """
        session = Session()
        try:
            combined_error = " | ".join(error_messages)
            resolution = session.query(ResolutionHistory).filter(ResolutionHistory.error_message == combined_error).first()
            return resolution
        except Exception as e:
            self.logger.error(f"Error checking resolution history: {e}")
            return None
        finally:
            session.close()

    def get_cached_user_decision(self, error_messages: list) -> Optional[str]:
        """
        Retrieves a cached user decision for similar error messages.

        Args:
            error_messages (list): List of error messages.

        Returns:
            Optional[str]: The cached user decision if available, or None if no recent match is found.
        """
        session = Session()
        try:
            combined_error = " | ".join(error_messages)

            # Define an expiration period for entries (e.g., 30 days)
            expiration_threshold = datetime.now(timezone.utc) - timedelta(days=30)

            # Fetch all recent cache entries
            recent_entries = session.query(UserDecisionCache).filter(
                UserDecisionCache.timestamp >= expiration_threshold
            ).all()

            # Find the closest match based on similarity
            best_match, best_similarity = None, 0
            for entry in recent_entries:
                similarity = SequenceMatcher(None, entry.error_message, combined_error).ratio()
                if similarity > self.SIMILARITY_THRESHOLD and similarity > best_similarity:
                    best_match, best_similarity = entry, similarity

            # Update usage metadata if a suitable match is found
            if best_match:
                best_match.usage_count += 1
                best_match.last_used = datetime.now(timezone.utc)
                session.commit()
                self.logger.info(f"Retrieved cached decision with {best_similarity:.2f} similarity for error: {combined_error}")
                return best_match.user_decision

            self.logger.info(f"No suitable cached decision found for error: {combined_error}")
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving cached user decision: {e}")
            return None
        finally:
            session.close()

    def cache_user_decision(self, error_message: str, user_decision: str):
        """
        Caches the user's decision with metadata, usage tracking, and dynamic retention based on frequency.

        Args:
            error_message (str): The error message.
            user_decision (str): The user's resolution decision.
        """
        session = Session()
        try:
            # Cleanup expired entries
            expiration_threshold = datetime.now(timezone.utc) - timedelta(days=30)
            session.query(UserDecisionCache).filter(
                UserDecisionCache.timestamp < expiration_threshold
            ).delete()
            session.commit()

            # Check for existing entry
            existing_entry = session.query(UserDecisionCache).filter(
                UserDecisionCache.error_message == error_message
            ).first()

            if existing_entry:
                # Update existing entry
                existing_entry.user_decision = user_decision
                existing_entry.usage_count += 1
                existing_entry.last_used = datetime.now(timezone.utc)
                self.logger.info(f"Updated cached user decision for error: {error_message}")
            else:
                # Add new entry
                cache_entry = UserDecisionCache(
                    error_message=error_message,
                    user_decision=user_decision,
                    timestamp=datetime.now(timezone.utc),
                    usage_count=1,
                    first_seen=datetime.now(timezone.utc),
                    last_used=datetime.now(timezone.utc)
                )
                session.add(cache_entry)
                self.logger.info(f"User decision cached for error: {error_message}")

            # Dynamic retention management
            self._manage_cache_size(session)

            session.commit()
        except Exception as e:
            self.logger.error(f"Error caching user decision: {e}")
            session.rollback()
        finally:
            session.close()

    def _manage_cache_size(self, session):
        """Manages the size of the user decision cache."""
        max_cache_size = 1000  # Set an arbitrary limit
        current_cache_size = session.query(UserDecisionCache).count()

        if current_cache_size > max_cache_size:
            # Remove entries with low usage or that haven't been used recently
            session.query(UserDecisionCache).filter(
                UserDecisionCache.usage_count < 3,
                UserDecisionCache.last_used < datetime.now(timezone.utc) - timedelta(days=7)
            ).delete()
            self.logger.info("Performed dynamic cleanup on cache due to size constraints.")

    def schedule_task(self, cron_expression: str, task_callable: Callable, task_data: dict, task_id: Optional[str] = None):
        """Schedules a recurring task based on a cron expression."""
        try:
            cron_trigger = CronTrigger.from_crontab(cron_expression)
            self.scheduler.add_job(task_callable, cron_trigger, kwargs={"task_data": task_data}, id=task_id)
            self.logger.info(f"Scheduled task '{task_id or task_callable.__name__}' with cron expression: {cron_expression}")
        except Exception as e:
            self.log_error(e)
            self.logger.error(f"Failed to schedule task with cron expression: {cron_expression}")

    def update_scheduled_task(self, task_id: str, new_cron_expression: str):
        """Updates an existing scheduled task with a new cron expression."""
        try:
            job = self.scheduler.get_job(task_id)
            if job:
                new_trigger = CronTrigger.from_crontab(new_cron_expression)
                job.reschedule(trigger=new_trigger)
                self.logger.info(f"Updated scheduled task '{task_id}' with new cron expression: {new_cron_expression}")
            else:
                self.logger.warning(f"Task '{task_id}' not found.")
        except Exception as e:
            self.log_error(e, {"task_id": task_id, "new_cron_expression": new_cron_expression})
            self.logger.error(f"Failed to update scheduled task '{task_id}'.")

    def remove_scheduled_task(self, task_id: str):
        """Removes a scheduled task by its task_id."""
        job = self.scheduler.get_job(task_id)
        if job:
            job.remove()
            self.logger.info(f"Removed scheduled task '{task_id}'.")
        else:
            self.logger.warning(f"Task '{task_id}' not found for removal.")

    def introduce(self) -> str:
        """Provides a brief introduction of the agent, including name and description."""
        introduction = f"I am {self.name}. {self.description}"
        self.logger.info("Introduction called.")
        return introduction

    def describe_capabilities(self) -> str:
        """Returns a description of the agent's capabilities."""
        capabilities_description = f"{self.name} can execute tasks related to {self.description}."
        self.logger.info("Capabilities described.")
        return capabilities_description

    def shutdown(self):
        """Gracefully shuts down the scheduler and closes database sessions."""
        self.scheduler.shutdown()
        self.logger.info("Scheduler shut down successfully.")

    # ------------------------
    # Memory and Performance Integration
    # ------------------------

    def run_query(self, prompt: str) -> str:
        """
        Run a query against Mistral 7B via Ollama and store the interaction in memory.

        Args:
            prompt (str): The user prompt to send to Mistral.

        Returns:
            str: The response from Mistral or an error message.
        """
        try:
            # Retrieve relevant memory context
            if self.memory_manager:
                memory_context = self.memory_manager.retrieve_memory(self.project_name, limit=5)
                complete_prompt = f"{memory_context}User: {prompt}\nAI:"
            else:
                complete_prompt = f"User: {prompt}\nAI:"

            self.logger.debug(f"Complete prompt sent to AI:\n{complete_prompt}")

            # Run the Ollama command with the complete prompt
            result = subprocess.run(
                ["ollama", "run", "mistral:latest", "--prompt", complete_prompt],
                capture_output=True,
                text=True,
                check=True
            )
            response = result.stdout.strip()
            self.logger.info(f"Received response from AI for prompt: '{prompt}'")

            # Save the interaction to memory
            if self.memory_manager:
                self.memory_manager.save_memory(self.project_name, prompt, response)

            # Log performance as success
            if self.performance_monitor:
                self.performance_monitor.log_performance(self.name, prompt, success=True, response=response)

            return response
        except subprocess.CalledProcessError as e:
            error_message = f"An error occurred while communicating with Ollama: {e.stdout.strip() or e.stderr.strip()}"
            self.logger.error(error_message)

            # Log performance as failure
            if self.performance_monitor:
                self.performance_monitor.log_performance(self.name, prompt, success=False, response=error_message)

            # Handle or cache based on error
            self._handle_error(prompt, error_message)

            return error_message
        except Exception as ex:
            error_message = f"An unexpected error occurred: {str(ex)}"
            self.logger.error(error_message)

            # Log performance as failure
            if self.performance_monitor:
                self.performance_monitor.log_performance(self.name, prompt, success=False, response=error_message)

            # Handle or cache based on error
            self._handle_error(prompt, error_message)

            return error_message

    def chat(self, user_input: str) -> str:
        """
        Facilitate a chat interaction with the AI agent.

        Args:
            user_input (str): Input from the user.

        Returns:
            str: Response from the AI agent.
        """
        self.logger.info(f"User input received: '{user_input}'")
        response = self.run_query(user_input)
        self.logger.info(f"AI response: '{response}'")

        # Analyze performance after each interaction
        self.self_improve()

        return response

    def _handle_error(self, prompt: str, error_message: str):
        """
        Handle errors by attempting to retrieve cached decisions or triggering self-improvement.

        Args:
            prompt (str): The original prompt that caused the error.
            error_message (str): The error message encountered.
        """
        # Attempt to retrieve a cached decision based on the error message
        similar_decision = self.get_cached_user_decision([error_message])
        if similar_decision:
            self.logger.info(f"Using cached decision for error: {error_message}")
            return similar_decision
        # Perform self-improvement or offer suggestion if no cached decision
        self.self_improve()
        # Optionally, cache a new decision based on the error
        # For example, prompt the user for a decision and cache it
        user_decision_input = input(f"Error encountered: {error_message}\nDo you want to provide a manual resolution? (y/n): ")
        if user_decision_input.lower() == 'y':
            manual_resolution = input("Please provide a manual resolution: ")
            self.save_resolution_history(error_message, user_decision=manual_resolution)
            self.cache_user_decision(error_message, manual_resolution)

    def self_improve(self):
        """
        Analyze performance and adjust operations to improve future interactions.
        This method embodies the self-improvement capability of the AI agent.
        """
        if not self.performance_monitor:
            self.logger.info("No PerformanceMonitor instance available for self-improvement.")
            return

        analysis = self.performance_monitor.analyze_performance(self.name)
        if not analysis:
            self.logger.info("No performance data available for self-improvement.")
            return

        success_rate = analysis.get('success_rate', 0)
        failures = analysis.get('failures', 0)

        self.logger.debug(f"Self-improvement analysis: {analysis}")

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
                self.logger.warning(f"Most common failure reason: {most_common_reason}")
                # Take action based on failure reason
                self.take_action_based_on_failure(most_common_reason)
        elif success_rate >= SUCCESS_THRESHOLD:
            self.logger.info("Performance is satisfactory. No immediate improvements needed.")
        else:
            self.logger.info("Performance analysis does not require immediate action.")

    def take_action_based_on_failure(self, reason: str):
        """
        Takes specific actions based on the identified failure reason.

        Args:
            reason (str): The most common failure reason.
        """
        self.logger.info(f"Taking action based on failure reason: {reason}")
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
        self.logger.info(suggestion)
        print(f"AI Suggestion: {suggestion}")

    def suggest_improvements(self):
        """
        Suggests improvements to its own operations based on performance data.
        """
        if not self.performance_monitor:
            self.logger.info("No PerformanceMonitor instance available to suggest improvements.")
            return

        analysis = self.performance_monitor.analyze_performance(self.name)
        if not analysis:
            self.logger.info("No performance data available to suggest improvements.")
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
            self.logger.info(suggestion_message)
            print(f"AI Suggestion: {suggestion_message}")
        else:
            self.logger.info("No improvements needed based on current performance data.")

    async def solve_task_with_reasoning(self, task: str) -> str:
        """
        Solves a task using advanced chain-of-thought reasoning.

        Args:
            task (str): The main task to solve.

        Returns:
            str: The final result after reasoning.
        """
        if not self.reasoner:
            self.logger.warning("ChainOfThoughtReasoner not initialized. Falling back to solve_task.")
            return self.solve_task({"type": "simple_task"})  # Adjust as necessary

        result = await self.reasoner.solve_task_with_reasoning(task, self.name)
        return result

    # Abstract method to be implemented by subclasses
    @abc.abstractmethod
    def solve_task(self, task_data: dict) -> str:
        """Abstract method to solve a task. Must be implemented by subclasses."""
        pass
