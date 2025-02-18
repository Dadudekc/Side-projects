"""

This Python script is used to automate the process of updating docstrings for Python files in a specified directory. The script uses OpenAI's GPT model to generate the docstrings. It reads each file, extracts any existing docstring, and if the file does not already have a docstring or if overwriting is set, creates a new one. It also backs up the original files before modifying them. It includes a mock mode for testing, where a hard-coded response is used instead of interacting
"""

import os
import shutil
import openai
import logging
import argparse
import time
import re

# === CONFIGURATION ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not set. Set it as an environment variable before running.")

# Default project settings
PROJECT_ROOT = "D:/side_projects/Side-projects/ai_agent_project"
DEFAULT_BACKUP_FOLDER = os.path.join(PROJECT_ROOT, "backup")
EXAMPLE_FILE = os.path.join(PROJECT_ROOT, "example.py")  # Example file for testing
LOG_FILE = os.path.join(PROJECT_ROOT, "log.txt")  # Log file

# Ensure backup folder exists
os.makedirs(DEFAULT_BACKUP_FOLDER, exist_ok=True)

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === OpenAI API Key Setup ===
openai.api_key = OPENAI_API_KEY

# === OpenAI Prompt Template ===
PROMPT_TEMPLATE = """
You are an expert software architect. Analyze the provided Python file and generate a concise module-level docstring.

- Summarize its purpose in 3-4 lines.
- If it's a utility, agent, or AI model, mention its primary function.
- Be clear, direct, and informative.

File Contents:
{code_snippet}

---

Generate a module docstring:
"""

# === Function to Generate Docstring via OpenAI ===
def get_openai_response(code_snippet, mock_mode=False):
    """Queries OpenAI to generate a module docstring or returns a mock response for testing."""
    if mock_mode:
        return "A utility module for managing and updating Python file docstrings using OpenAI."

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Generate a docstring for the following Python code:"},
                    {"role": "user", "content": code_snippet}
                ],
                max_tokens=100
            )
            return response["choices"][0]["message"]["content"].strip()

        except Exception as e:
            logging.error(f"⚠ OpenAI API call failed (Attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(2)  # Small delay before retry

    return None  # Return None if all retries fail

# === Extract Existing Docstring ===
def extract_existing_docstring(file_content):
    """
    Extracts the module-level docstring from a Python file.
    
    Returns:
        docstring (str or None): The extracted docstring, if found.
        remaining_code (str): The rest of the file content without the docstring.
    """
    docstring_match = re.match(r'^[\'\"]{3}(.*?)[\'\"]{3}', file_content, re.DOTALL)
    
    if docstring_match:
        extracted_docstring = docstring_match.group(1).strip()
        remaining_code = file_content[docstring_match.end():].strip()
        return extracted_docstring, remaining_code
    return None, file_content.strip()

# === Insert or Update Docstring in a File ===
def insert_or_update_docstring(file_path, backup_folder, skip_existing, mock_mode=False):
    """Inserts or updates the module-level docstring in a Python file."""
    if file_path.endswith("__init__.py"):
        logging.info(f"🚫 Skipping {file_path} (init file)")
        return  # Skip __init__.py files

    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    existing_docstring, remaining_code = extract_existing_docstring(file_content)

    # If skipping existing docstrings and one is already found, do nothing
    if skip_existing and existing_docstring:
        logging.info(f"✅ Skipping {file_path} (Already contains a module docstring)")
        return

    if not remaining_code.strip():
        logging.warning(f"⚠ Skipping empty file: {file_path}")
        return

    new_docstring = get_openai_response(remaining_code, mock_mode=mock_mode)
    if not new_docstring:
        logging.warning(f"⚠ Skipping update for {file_path} (Failed to generate docstring)")
        return

    # Remove extra triple quotes if present
    new_docstring = new_docstring.strip('"').strip("'")

    formatted_docstring = f'"""\n{new_docstring}\n"""'

    # Backup before modifying
    backup_path = os.path.join(backup_folder, os.path.basename(file_path) + ".bak")
    shutil.copy(file_path, backup_path)
    logging.info(f"📂 Backup saved to: {backup_path}")

    # Combine the new docstring with the rest of the code
    updated_code = f"{formatted_docstring}\n\n{remaining_code}\n"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_code)
        f.flush()
        os.fsync(f.fileno())

    logging.info(f"✅ Updated: {file_path}")

# === Process All Python Files in the Project ===
def process_project(root_dir, backup_folder, skip_existing, mock_mode=False):
    """Iterates through the project and updates all Python files."""
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                insert_or_update_docstring(file_path, backup_folder, skip_existing, mock_mode)

# === MAIN EXECUTION WITH ARGPARSE ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate docstring updates for Python files.")
    parser.add_argument("--dir", type=str, default=PROJECT_ROOT, help="Root directory to process (default: project root)")
    parser.add_argument("--backup-dir", type=str, default=DEFAULT_BACKUP_FOLDER, help="Folder to store backups (default: backup/)")
    parser.add_argument("--skip-existing", action="store_true", help="Skip updating files that already contain the correct docstring")
    parser.add_argument("--mock", action="store_true", help="Use mock response instead of OpenAI API")

    args = parser.parse_args()

    print("\n🔍 Running OpenAI response test on a single file before full execution...")
    insert_or_update_docstring(EXAMPLE_FILE, args.backup_dir, args.skip_existing, mock_mode=args.mock)

    user_input = input("\nProceed with updating all files? (yes/no): ").strip().lower()
    if user_input == "yes":
        process_project(args.dir, args.backup_dir, args.skip_existing, mock_mode=args.mock)
        print("\n🎯 All Python files have been processed and updated with module-level docstrings.")
    else:
        print("\n❌ Update aborted. Only the test file was modified.")
