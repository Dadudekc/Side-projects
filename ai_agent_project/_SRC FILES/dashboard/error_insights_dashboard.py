# -------------------------------------------------------------------
# File Path: C:\Projects\AI_Debugger_Assistant\src\dashboard\error_insights_dashboard.py
#
# Project: AI_Debugger_Assistant
#
# Description:
# This script generates an intelligent error insights dashboard that aggregates,
# categorizes, and analyzes error data from multiple debugging agents. The dashboard 
# provides actionable insights, trend analysis, and success metrics, giving users 
# a powerful tool to understand error patterns, track fixes, and optimize resolution 
# strategies.
# -------------------------------------------------------------------

import logging
import datetime
from collections import Counter
from typing import Dict, List, Tuple
from agents.core.utilities.debugger_agent import DebuggerAgent
from agents.tasks.journal_agent import JournalAgent
from ai_agent_project.src.utilities.analytics_manager import AnalyticsManager  # Custom analytics utility
from ai_agent_project.src.utilities.alert_manager import AlertManager  # Custom alerting utility

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ErrorInsightsDashboard")

class ErrorInsightsDashboard:
    """
    Generates a dashboard of insights from debugging errors, offering metrics, trends, 
    and recommended actions to improve system stability and efficiency.
    """

    def __init__(self):
        self.debugger_agent = DebuggerAgent()
        self.journal_agent = JournalAgent()
        self.analytics_manager = AnalyticsManager()
        self.alert_manager = AlertManager()
        self.error_logs = []  # Store error logs for aggregation
        logger.info("Error Insights Dashboard initialized.")

    def log_error(self, error_message: str, task: str, severity: str):
        """
        Logs errors into the dashboard for aggregation and analysis.

        Args:
            error_message (str): Description of the error.
            task (str): The associated task name.
            severity (str): Severity level (e.g., 'Critical', 'Moderate', 'Low').
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "error_message": error_message,
            "task": task,
            "severity": severity
        }
        self.error_logs.append(log_entry)
        logger.info(f"Logged error for task '{task}': {error_message} with severity '{severity}'.")

        # Trigger alert for critical issues
        if severity == "Critical":
            self.alert_manager.send_alert(f"Critical issue detected in task '{task}': {error_message}")

    def generate_error_insights(self) -> Dict[str, Any]:
        """
        Aggregates and analyzes error data, returning insights including most 
        common errors, trending issues, and severity distribution.

        Returns:
            dict: A dictionary of aggregated insights and metrics.
        """
        error_messages = [log["error_message"] for log in self.error_logs]
        tasks = [log["task"] for log in self.error_logs]
        severity_levels = [log["severity"] for log in self.error_logs]

        insights = {
            "total_errors": len(self.error_logs),
            "most_common_errors": Counter(error_messages).most_common(5),
            "trending_tasks": Counter(tasks).most_common(3),
            "severity_distribution": Counter(severity_levels)
        }
        logger.info(f"Generated error insights: {insights}")
        return insights

    def recommend_actions(self) -> List[Tuple[str, str]]:
        """
        Provides recommended actions based on error patterns and historical 
        resolutions, prioritizing high-severity or frequent errors.

        Returns:
            list: List of recommended actions for high-priority errors.
        """
        recommendations = []
        common_errors = [error for error, _ in Counter([log["error_message"] for log in self.error_logs]).most_common(3)]
        
        for error in common_errors:
            resolution = self.debugger_agent.solve_task(task="suggest_resolution", error=error)
            recommendations.append((error, resolution))
        
        logger.info(f"Recommended actions generated: {recommendations}")
        return recommendations

    def track_resolution_effectiveness(self):
        """
        Analyzes the effectiveness of past resolutions, tracking metrics like 
        resolution time, recurrence rate, and the success of applied fixes.
        """
        resolution_data = self.journal_agent.list_journal_entries()
        effectiveness = self.analytics_manager.evaluate_resolution_effectiveness(resolution_data)
        
        logger.info(f"Resolution effectiveness metrics: {effectiveness}")
        return effectiveness

    def display_dashboard(self):
        """
        Displays the insights and recommended actions as a simulated dashboard output.
        """
        insights = self.generate_error_insights()
        recommendations = self.recommend_actions()
        effectiveness_metrics = self.track_resolution_effectiveness()

        # Simulated dashboard display (replace with actual UI in a full implementation)
        print("\n--- Error Insights Dashboard ---")
        print(f"Total Errors Logged: {insights['total_errors']}")
        print(f"Most Common Errors: {insights['most_common_errors']}")
        print(f"Trending Tasks: {insights['trending_tasks']}")
        print(f"Severity Distribution: {insights['severity_distribution']}")
        print("\n--- Recommended Actions ---")
        for error, resolution in recommendations:
            print(f"Error: {error} | Recommended Resolution: {resolution}")
        print("\n--- Resolution Effectiveness Metrics ---")
        print(effectiveness_metrics)

        # Optional: send alert if metrics show critical trends
        if insights['severity_distribution'].get("Critical", 0) > 5:
            self.alert_manager.send_alert("High number of critical issues detected in system.")

if __name__ == "__main__":
    dashboard = ErrorInsightsDashboard()

    # Example error logs
    dashboard.log_error("Database connection timeout", "Fetch Data", "Critical")
    dashboard.log_error("Null value error in user profile", "Update Profile", "Moderate")
    dashboard.log_error("API request failed", "Fetch Data", "Critical")
    dashboard.log_error("Memory limit exceeded", "Run Analysis", "High")
    
    # Display the dashboard insights
    dashboard.display_dashboard()
