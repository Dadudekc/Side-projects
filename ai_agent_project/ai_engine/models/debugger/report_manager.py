import json
import logging
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional

class ReportManager:
    """Manages structured reports for debugging, test results, and analytics."""

    REPORTS_DIR = "reports/"
    LOG_FILE = "reports/report_manager.log"
    MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_BACKUP_LOGS = 3

    def __init__(self):
        os.makedirs(self.REPORTS_DIR, exist_ok=True)
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Configures structured logging with log rotation while preventing test locks."""
        self._release_log_handlers()

        # During tests, log to console instead of file
        if "pytest" in os.environ.get("_", "") or "unittest" in os.environ.get("_", ""):
            handler = logging.StreamHandler()
        else:
            if os.path.exists(self.LOG_FILE) and os.path.getsize(self.LOG_FILE) > self.MAX_LOG_SIZE:
                self._rotate_logs()
            handler = logging.FileHandler(self.LOG_FILE, encoding="utf-8")

        logger = logging.getLogger("ReportManager")
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(handler)

        return logger

    def _release_log_handlers(self):
        """Releases all log handlers to prevent file locking issues."""
        logger = logging.getLogger("ReportManager")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    def _rotate_logs(self):
        """Rotates old logs to prevent excessive file size."""
        for i in range(self.MAX_BACKUP_LOGS, 0, -1):
            old_log = f"{self.LOG_FILE}.{i}"
            new_log = f"{self.LOG_FILE}.{i+1}"
            if os.path.exists(old_log):
                os.rename(old_log, new_log)
        shutil.move(self.LOG_FILE, f"{self.LOG_FILE}.1")

    def _generate_filename(self, base_name: str) -> str:
        """Generates a unique filename based on timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.json"

    def save_report(self, base_filename: str, data: Dict):
        """
        Saves a structured JSON report with automatic versioning.
        
        Args:
            base_filename (str): Name of the report without extension.
            data (Dict): The report data.
        """
        filename = self._generate_filename(base_filename)
        filepath = os.path.join(self.REPORTS_DIR, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            self.logger.info(f"✅ Report saved: {filename}")
        except Exception as e:
            self.logger.error(f"❌ Error saving report {filename}: {e}")

    def load_report(self, filename: str) -> Optional[Dict]:
        """
        Loads a JSON report by filename.
        
        Args:
            filename (str): The report filename.
            
        Returns:
            Optional[Dict]: The report data if found, else None.
        """
        filepath = os.path.join(self.REPORTS_DIR, filename)
        
        if not os.path.exists(filepath):
            self.logger.warning(f"⚠️ Report not found: {filename}")
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Error loading report {filename}: Invalid JSON - {e}")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error loading report {filename}: {e}")
        
        return None

    def list_reports(self) -> List[str]:
        """
        Returns a list of all available reports.
        
        Returns:
            List[str]: List of report filenames.
        """
        reports = sorted(f for f in os.listdir(self.REPORTS_DIR) if f.endswith(".json"))
        self.logger.info(f"📂 {len(reports)} reports found.")
        return reports

    def search_reports(self, keyword: str) -> List[str]:
        """
        Searches reports for a specific keyword in the filename or content.
        
        Args:
            keyword (str): The keyword to search for.
            
        Returns:
            List[str]: Filenames of matching reports.
        """
        matches = []
        for filename in self.list_reports():
            if keyword.lower() in filename.lower():
                matches.append(filename)
                continue
            data = self.load_report(filename)
            if data and any(keyword.lower() in str(value).lower() for value in data.values()):
                matches.append(filename)

        self.logger.info(f"🔍 Found {len(matches)} reports matching '{keyword}'.")
        return matches

    def delete_old_reports(self, days: int = 30):
        """
        Deletes reports older than a specified number of days.
        
        Args:
            days (int): Number of days before reports are considered old.
        """
        cutoff_date = datetime.now().timestamp() - (days * 86400)
        deleted_files = []

        for filename in self.list_reports():
            filepath = os.path.join(self.REPORTS_DIR, filename)
            if os.path.getmtime(filepath) < cutoff_date:
                os.remove(filepath)
                deleted_files.append(filename)

        self.logger.info(f"🗑️ Deleted {len(deleted_files)} old reports older than {days} days.")

    def log_entry(self, message: str, level="info"):
        """
        Logs a structured message into the report log file.
        
        Args:
            message (str): Log message.
            level (str): Log level ('info', 'warning', 'error', 'critical').
        """
        log_methods = {
            "info": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error,
            "critical": self.logger.critical,
        }
        log_methods.get(level, self.logger.info)(message)


if __name__ == "__main__":
    manager = ReportManager()

    # 🔥 Example Usage
    test_report = {
        "test_name": "UnitTest AI Model",
        "status": "passed",
        "timestamp": datetime.now().isoformat(),
        "details": {"accuracy": 0.95, "time_elapsed": "3.2s"}
    }

    manager.save_report("ai_test_report", test_report)
    print("Available Reports:", manager.list_reports())

    loaded_report = manager.load_report(manager.list_reports()[0])
    print("Loaded Report:", loaded_report)

    # Search Reports
    search_results = manager.search_reports("AI")
    print("Search Results:", search_results)

    # Delete old reports
    manager.delete_old_reports(days=30)
