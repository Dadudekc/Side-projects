import os
import subprocess
import logging
import shutil
import time
import sqlite3
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# === Configuration ===
USE_PARALLEL_PROCESSING = True  # For faster processing of many files
MAX_RETRIES = 3                 # AI call retry count
SLEEP_BETWEEN_RETRIES = 2       # Delay between retries (seconds)
GIT_COMMIT_RANGE = "HEAD~1"     # If None, scan entire project

# === Logging Setup ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AIRefactorAgent")

# === Database Setup ===
DB_FILE = "ai_refactor_reviews.db"
def initialize_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refactor_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                original_code TEXT,
                ai_suggestion TEXT,
                human_feedback TEXT DEFAULT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def save_ai_suggestion(file_name, original_code, ai_suggestion):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO refactor_reviews (file_name, original_code, ai_suggestion)
            VALUES (?, ?, ?)
        """, (file_name, original_code, ai_suggestion))
        conn.commit()

# === File Detection ===
def get_python_files():
    """
    Returns a list of all Python files in the project directory,
    including those in subdirectories.
    """
    python_files = []

    def scan_directory(directory):
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith(".py"):
                    python_files.append(os.path.relpath(entry.path, "."))
                elif entry.is_dir():
                    scan_directory(entry.path)
    scan_directory(".")
    logger.info("Files to refactor: %s", python_files)
    return python_files

# === Backup & Restore ===
def backup_file(file_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.bak.{timestamp}"
    try:
        shutil.copyfile(file_path, backup_path)
        logger.info("Backup created: %s", backup_path)
        return backup_path
    except Exception as e:
        logger.error("Error creating backup for %s: %s", file_path, e)
        return None

def restore_backup(file_path):
    backup_files = sorted([f for f in os.listdir(".") if f.startswith(f"{file_path}.bak")], reverse=True)
    if backup_files:
        latest_backup = backup_files[0]
        shutil.copyfile(latest_backup, file_path)
        logger.info("Restored backup: %s → %s", latest_backup, file_path)
    else:
        logger.warning("No backup found to restore for %s", file_path)

# === AI Refactoring for Files ===
def analyze_code_with_ollama(file_path):
    """
    Uses the Ollama CLI with the mistral:latest model to analyze and refactor code.
    Returns a tuple (original_code, ai_suggestion) if successful; otherwise, (original_code, None).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_code = f.read()
    except Exception as e:
        logger.error("Error reading file %s: %s", file_path, e)
        return None, None

    prompt = f"""
You are a professional Python refactoring assistant. Your task is to refactor the following Python code to:
- Optimize performance and execution speed.
- Simplify complex logic.
- Improve readability.
- Identify and fix potential bugs.
- Ensure best practices are followed.

Return only the refactored code.

Code:
{original_code}
"""
    command = ["ollama", "run", "mistral:latest"]
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                check=True
            )
            ai_suggestion = result.stdout.strip()
            if ai_suggestion:
                logger.info("Received refactored code for %s", file_path)
                return original_code, ai_suggestion
            else:
                logger.warning("Empty AI response on attempt %d for %s", attempt, file_path)
        except subprocess.CalledProcessError as e:
            logger.error("Ollama error on attempt %d for %s: %s", attempt, file_path, e)
            logger.error("Stdout:\n%s\nStderr:\n%s", e.stdout, e.stderr)
        if attempt < MAX_RETRIES:
            time.sleep(SLEEP_BETWEEN_RETRIES)
    return original_code, None

def process_file(file_path):
    logger.info("Processing file: %s", file_path)
    backup = backup_file(file_path)
    if not backup:
        logger.error("Skipping %s due to backup failure.", file_path)
        return
    original_code, ai_suggestion = analyze_code_with_ollama(file_path)
    if ai_suggestion:
        save_ai_suggestion(file_path, original_code, ai_suggestion)
        logger.info("AI refactor stored for human review: %s", file_path)
    else:
        logger.warning("No AI refactored code generated for %s. Original file left intact.", file_path)

def refactor_files():
    files_to_process = get_python_files()
    if not files_to_process:
        return
    if USE_PARALLEL_PROCESSING:
        with ThreadPoolExecutor() as executor:
            executor.map(process_file, files_to_process)
    else:
        for file_path in files_to_process:
            process_file(file_path)

# === Human Review Process ===
def get_human_feedback():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, file_name, ai_suggestion FROM refactor_reviews WHERE human_feedback IS NULL")
        reviews = cursor.fetchall()
    return reviews

def submit_human_feedback(review_id, feedback):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE refactor_reviews SET human_feedback = ? WHERE id = ?", (feedback, review_id))
        conn.commit()

def review_pending_suggestions():
    pending_reviews = get_human_feedback()
    if not pending_reviews:
        logger.info("No pending AI refactor reviews.")
        return
    for review in pending_reviews:
        review_id, file_name, ai_suggestion = review
        print(f"\nFile: {file_name}")
        print("AI Suggestion:\n", ai_suggestion)
        feedback = input("Approve (y) / Reject (n) / Edit (e): ").strip().lower()
        if feedback == "y":
            submit_human_feedback(review_id, "approved")
        elif feedback == "n":
            submit_human_feedback(review_id, "rejected")
        elif feedback == "e":
            new_suggestion = input("Provide your edited version:\n")
            submit_human_feedback(review_id, f"edited: {new_suggestion}")
        else:
            print("Invalid input, skipping.")

# === Performance Logging ===
def update_performance_log(refactored_files):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "files_refactored": len(refactored_files),
        "files": refactored_files
    }
    log_data = []
    log_file = "refactor_log.json"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Corrupt log file. Resetting log.")
    log_data.append(log_entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=4)
    logger.info("Refactor log updated.")

def run_agent():
    refactor_files()
    review_pending_suggestions()

# === Function-Level Refactoring ===
def refactor_function_with_ai(function_data):
    """
    Uses AI (Ollama) to refactor a function and return the improved version.
    """
    prompt = f"""
    You are a Python refactoring assistant. Your job is to optimize the following function:
    - Improve performance
    - Enhance readability
    - Remove redundant code
    - Follow best practices
    - Keep function behavior unchanged

    Function:
    ```
    {function_data['code']}
    ```
    Return only the refactored function.
    """
    try:
        result = subprocess.run(["ollama", "run", "mistral", prompt], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Error running AI refactor: {e}")
        return None

def apply_refactored_function(original_function, refactored_function):
    """
    Replaces the original function with the refactored version in the source file.
    """
    file_path = original_function["file"]
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    start, end = original_function["start_line"] - 1, original_function["end_line"]
    lines[start:end] = [refactored_function + "\n"]
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ Refactored function {original_function['name']} in {file_path}")

def iteratively_refactor_project():
    """
    Iteratively improves the project function by function.
    Extracts function definitions from 'function_map.json', refactors each function,
    and applies changes if tests pass.
    """
    with open("function_map.json", "r", encoding="utf-8") as f:
        functions = json.load(f)
    
    for function in functions:
        print(f"🔍 Refactoring {function['name']} in {function['file']}...")
        with open(function["file"], "r", encoding="utf-8") as f:
            lines = f.readlines()
        function_code = "".join(lines[function["start_line"] - 1 : function["end_line"]])
        function["code"] = function_code
        refactored_function = refactor_function_with_ai(function)
        if refactored_function:
            apply_refactored_function(function, refactored_function)
            # Run tests after each change to validate the change
            test_result = subprocess.run(["pytest", "test_workspace"], capture_output=True, text=True)
            print(test_result.stdout)
            if "FAILED" in test_result.stdout:
                print(f"❌ Reverting changes for {function['name']} due to failed tests.")
                apply_refactored_function(function, function_code)
            else:
                print(f"✅ Function {function['name']} refactored successfully!")
    
    print("🚀 Iterative AI refactoring complete!")

# === Main Execution ===
if __name__ == "__main__":
    initialize_database()
    run_agent()
    # Uncomment the line below to run iterative function-level refactoring:
    # iteratively_refactor_project()
