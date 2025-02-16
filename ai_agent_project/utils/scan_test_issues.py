import logging
import os
import subprocess
from typing import List, Dict, Any

# Configure detailed logging
logging.basicConfig(
    filename='debug_log.log',  # Save logs to a file for better tracking
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger("DebugManager")

class DebugManager:
    """
    Manages debugging, import issue detection, and logging.
    """
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.abspath(__file__))
    
    def run_tests(self) -> List[Dict[str, Any]]:
        """
        Runs pytest and captures failures with detailed logging.
        """
        logger.info("🚀 Running tests with detailed logging...")
        result = subprocess.run(["pytest", "tests", "--disable-warnings"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ All tests passed!")
            return []
        
        logger.error(f"❌ Tests failed. Capturing errors.\n{result.stdout}")
        return self.parse_failures(result.stdout)
    
    def parse_failures(self, output: str) -> List[Dict[str, Any]]:
        """
        Extracts error messages and logs them.
        """
        failures = []
        for line in output.split("\n"):
            if "ERROR collecting" in line or "ModuleNotFoundError" in line:
                logger.error(f"⚠️ {line}")
                failures.append({"error": line})
        return failures
    
    def scan_import_issues(self):
        """
        Scans the project for import errors and logs them.
        """
        logger.info("🔍 Scanning for import issues...")
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        subprocess.run(["python", "-m", "py_compile", file_path], capture_output=True, text=True, check=True)
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Import issue in {file_path}: {e.stderr}")
    
if __name__ == "__main__":
    manager = DebugManager()
    manager.scan_import_issues()
    failures = manager.run_tests()
    if failures:
        logger.info("📌 Review debug_log.log for details on failures.")
