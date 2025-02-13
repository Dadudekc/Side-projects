# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\agents\orchestrator\debugging_orchestrator.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This script orchestrates AI-assisted debugging sessions, utilizing 
# multiple agents to handle debugging, task planning, journal entry 
# management, and automated reporting. It aims to streamline the 
# troubleshooting process with AI-driven insights, while maintaining 
# a comprehensive record of each session.
#
# Key Functionalities:
# 1. Debugging Workflow: Automated analysis, error resolution, and task tracking.
# 2. Journal Management: Logging, reflection prompts, and journaling via the JournalAgent.
# 3. Task Execution: Assigning and prioritizing tasks using TaskAgent.
# 4. Future-Ready Design: Easy to integrate with NLP for enhanced logging and task insights.
# -------------------------------------------------------------------

import logging
import datetime
from agents.core.utilities.debugger_agent import DebuggerAgent
from agents.tasks.journal_agent import JournalAgent
from agents.core.agent_dispatcher import AgentDispatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DebuggingOrchestrator")

class DebuggingOrchestrator:
    """
    A central controller for managing AI-assisted debugging sessions.
    Combines functionalities from DebuggerAgent, JournalAgent, and TaskAgent
    for streamlined, documented debugging and troubleshooting workflows.
    """

    def __init__(self):
        self.debugger_agent = DebuggerAgent()
        self.journal_agent = JournalAgent()
        self.dispatcher = AgentDispatcher()
        
        # Initialize agents or necessary components
        logger.info("Debugging Orchestrator initialized with DebuggerAgent and JournalAgent.")

    def start_debugging_session(self, task_description: str, error_log: str):
        """
        Initiates a debugging session with a task description and error log.
        
        Args:
            task_description (str): Description of the task to debug.
            error_log (str): Initial error message to analyze.
        """
        session_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Starting debugging session for task: {task_description}")
        
        # Step 1: Log the session start in Journal
        self.journal_agent.create_journal_entry(
            title=f"Debugging Session - {task_description}",
            content=f"Session started at {session_start_time}. Error log: {error_log}",
            tags=["debugging", "AI-assisted", task_description]
        )
        
        # Step 2: Analyze error using DebuggerAgent
        analysis_result = self.debugger_agent.solve_task(
            task="analyze_error", error=error_log
        )
        logger.info(f"Error analysis completed: {analysis_result}")
        
        # Step 3: Create task planning in Dispatcher
        task_data = {
            "task": task_description,
            "analysis_result": analysis_result,
            "priority": "High",
            "use_chain_of_thought": True
        }
        self.dispatcher.dispatch_task(**task_data)
        
        # Step 4: Log analysis result in Journal
        self.journal_agent.update_journal_entry(
            title=f"Debugging Session - {task_description}",
            new_content=f"Analysis result: {analysis_result}"
        )
        
        logger.info(f"Debugging session for '{task_description}' logged successfully.")

    def resolve_and_document(self, resolution_steps: str):
        """
        Resolves errors with provided steps and documents in journal.
        
        Args:
            resolution_steps (str): Steps taken to resolve the error.
        """
        # Step 5: Log resolution steps
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.journal_agent.create_journal_entry(
            title="Resolution Steps",
            content=f"Resolution completed at {timestamp} with steps: {resolution_steps}",
            tags=["resolution", "AI-assisted"]
        )
        
        logger.info("Resolution steps documented successfully.")

    def summarize_session(self, task_description: str):
        """
        Summarizes the session and completes the journal entry.
        
        Args:
            task_description (str): Description of the task being summarized.
        """
        # Step 6: Complete the session in Journal with summary
        session_summary = f"Debugging session for '{task_description}' has been completed."
        self.journal_agent.update_journal_entry(
            title=f"Debugging Session - {task_description}",
            new_content=session_summary
        )
        
        logger.info("Debugging session summary documented.")

    def perform_scheduled_backup(self):
        """
        Backup journal entries as part of scheduled maintenance.
        """
        backup_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_content = self.journal_agent.list_journal_entries()
        
        self.journal_agent.create_journal_entry(
            title=f"Backup - {backup_timestamp}",
            content=str(backup_content),
            tags=["backup", "maintenance"]
        )
        
        logger.info("Scheduled backup completed successfully.")


if __name__ == "__main__":
    orchestrator = DebuggingOrchestrator()
    # Example session start
    orchestrator.start_debugging_session(
        task_description="Fix database connection issue",
        error_log="Database connection timeout on port 5434"
    )
    # Example resolution documentation
    orchestrator.resolve_and_document(
        resolution_steps="Updated connection string, verified network access, restarted database service."
    )
    # Example session summary
    orchestrator.summarize_session(task_description="Fix database connection issue")
    # Perform a scheduled backup
    orchestrator.perform_scheduled_backup()

# -------------------------------------------------------------------
# Future Improvements
# -------------------------------------------------------------------
# 1. **Automated Task Prioritization**:
#    Implement a priority system to dynamically assess task urgency based on error severity and project deadlines.
#
# 2. **Integration with Alerts**:
#    Add support for sending alerts (e.g., email, Slack) when a critical error occurs or when a task fails multiple times.
#
# 3. **Enhanced AI Suggestions**:
#    Improve error analysis by integrating with external NLP tools for deeper diagnostics and resolution recommendations.
#
# 4. **Adaptive Task Management**:
#    Automatically adjust task priority or suggest reassignment based on performance data from the PerformanceMonitor.
#
# 5. **Scheduled Cleanups and Optimization**:
#    Schedule periodic cleanups for old logs and optimize the journal directory to keep file sizes manageable.
# -------------------------------------------------------------------
