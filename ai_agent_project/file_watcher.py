"""

This script monitors a directory containing tests (`TESTS_DIR`) and backs them up in real time to another directory (`BACKUP_DIR`). It uses the watchdog library to observe changes and trigger events when files are created, modified, or deleted. This script also interacts with the psutil library to list processes that may have modified the files.

If a test file is deleted, it is automatically restored from the backup directory, if a backup exists. Temporary and unnecessary files and directories (listed in `IGNORE
"""

import os
import time
import shutil
import psutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
LOG_FILE = "deletion_log.txt"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# Directories
TESTS_DIR = "tests"
BACKUP_DIR = "tests_backup"

# Ignore unnecessary directories and temporary files
IGNORED_DIRS = ["__pycache__", ".pytest_cache"]
IGNORED_EXTENSIONS = [".pyc", ".log"]

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

class TestFileWatcher(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.snapshot = self._take_snapshot()

    def _take_snapshot(self):
        """Create a snapshot of the current test files."""
        return {f: os.stat(os.path.join(TESTS_DIR, f)).st_mtime for f in os.listdir(TESTS_DIR) if os.path.isfile(os.path.join(TESTS_DIR, f))}

    def _get_process_info(self):
        """Returns a list of active processes that might have modified files."""
        processes = []
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            try:
                processes.append(f"PID {proc.info['pid']}: {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return processes

    def restore_file(self, file_path):
        """Restore a deleted file from the backup directory if it exists."""
        backup_file = os.path.join(BACKUP_DIR, os.path.basename(file_path))
        if os.path.exists(backup_file):
            shutil.copy(backup_file, file_path)
            logging.info(f"✅ Restored {file_path} from backup.")

    def on_deleted(self, event):
        """Handle deleted files and restore them if necessary."""
        if event.is_directory or any(ignored in event.src_path for ignored in IGNORED_DIRS) or event.src_path.endswith(tuple(IGNORED_EXTENSIONS)):
            return

        file_path = event.src_path
        logging.warning(f"❌ File deleted: {file_path}")
        logging.warning(f"🔍 Active Processes at deletion: {self._get_process_info()}")

        # Restore the file if it was a test file
        if os.path.basename(file_path) in self.snapshot:
            self.restore_file(file_path)

    def on_modified(self, event):
        """Detect modifications to test files."""
        if event.is_directory or any(ignored in event.src_path for ignored in IGNORED_DIRS) or event.src_path.endswith(tuple(IGNORED_EXTENSIONS)):
            return

        file_path = event.src_path
        logging.info(f"✏️ File modified: {file_path}")
        logging.info(f"🔍 Active Processes at modification: {self._get_process_info()}")

        # Create a backup of modified file
        time.sleep(0.2)  # Prevent race conditions
        if os.path.exists(file_path):
            backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
            shutil.copy(file_path, backup_path)
            logging.info(f"✅ Modified file backed up: {backup_path}")

    def on_created(self, event):
        """Log newly created files and back them up."""
        if event.is_directory or any(ignored in event.src_path for ignored in IGNORED_DIRS) or event.src_path.endswith(tuple(IGNORED_EXTENSIONS)):
            return

        file_path = event.src_path
        logging.info(f"📂 New file created: {file_path}")

        # Wait briefly in case file is still being written
        time.sleep(0.2)

        if os.path.exists(file_path):
            backup_path = os.path.join(BACKUP_DIR, os.path.basename(file_path))
            shutil.copy(file_path, backup_path)
            logging.info(f"✅ New file backed up: {backup_path}")
        else:
            logging.warning(f"⚠️ File vanished before backup: {file_path}")

def start_watching():
    """Starts the real-time file watcher."""
    if not os.path.exists(TESTS_DIR):
        logging.error(f"❌ Watched directory does not exist: {TESTS_DIR}")
        return

    event_handler = TestFileWatcher()
    observer = Observer()
    observer.schedule(event_handler, TESTS_DIR, recursive=True)
    observer.start()

    logging.info("🔍 Test file watcher started... Monitoring for changes.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("🛑 Test file watcher stopped.")

    observer.join()

if __name__ == "__main__":
    start_watching()
