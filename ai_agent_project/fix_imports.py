import os
import re

# Define project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Fix import in `test_ai_agent_utils.py`
def fix_test_ai_agent_utils():
    file_path = os.path.join(PROJECT_ROOT, "tests", "test_ai_agent_utils.py")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace the incorrect import
        new_content = re.sub(
            r"from ai_agent_utils import (.+)",
            r"from agents.core.utilities.ai_agent_utils import \1",
            content
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ Fixed import in {file_path}")

# Run tests
def run_tests():
    print("\n🚀 Running tests...\n")
    os.system("python run_tests.py")

# Main execution
if __name__ == "__main__":
    print("\n🔧 Fixing import in test_ai_agent_utils.py...")
    fix_test_ai_agent_utils()

    print("\n✅ Fix applied successfully. Running tests...")
    run_tests()
