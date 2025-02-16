import os
import re

# Define the project directory
PROJECT_DIR = "D:/side_projects/Side-projects/ai_agent_project/tests"

# Common fixes without lookbehind assertions
fix_patterns = [
    (r'"""{3,}', '"""'),  # Fix malformed docstrings
    (r'"""(.*?)"""', r'"""\1"""', re.DOTALL),  # Ensure docstrings are well-formed
    (r'"""(.*?)$', r'"""\1"""', re.MULTILINE),  # Fix unterminated docstrings
    (r'\bAIModelManager\b', 'from ai_model_manager import AIModelManager\nAIModelManager', re.MULTILINE),  # Fix missing AIModelManager import
    (r'\bMemoryManager\b', 'from memory_manager import MemoryManager\nMemoryManager', re.MULTILINE),  # Fix missing MemoryManager import
    (r'\bAI_CONFIDENCE_FILE\b', 'from ai_confidence_manager import AI_CONFIDENCE_FILE\nAI_CONFIDENCE_FILE', re.MULTILINE),  # Fix missing AI_CONFIDENCE_FILE import
    (r'\bAgentRegistry\b', 'from agent_registry import AgentRegistry\nAgentRegistry', re.MULTILINE),  # Fix missing AgentRegistry import
    (r'\bDebuggerCore\b', 'from debugger_core import DebuggerCore\nDebuggerCore', re.MULTILINE),  # Fix missing DebuggerCore import
    (r'(\U0001f539)', ''),  # Remove Unicode characters causing errors
    (r'\b(\w+)\n\s*\^+', ''),  # Remove syntax error caret markers from logs
]

# Function to process files
def fix_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        original_content = content  # Store original content for comparison
        
        # Apply regex fixes
        for pattern, replacement, *flags in fix_patterns:
            content = re.sub(pattern, replacement, content, flags=flags[0] if flags else 0)

        # Save only if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"✅ Fixed: {file_path}")

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

# Scan all test files and apply fixes
for root, _, files in os.walk(PROJECT_DIR):
    for file in files:
        if file.endswith(".py"):
            fix_file(os.path.join(root, file))

print("🎯 All possible fixes have been applied. Re-run your tests!") 
