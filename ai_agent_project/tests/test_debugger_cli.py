import unittest
import subprocess
import json
import os

AI_PERFORMANCE_FILE = "ai_performance.json"

class TestDebuggerCLI(unittest.TestCase):
    """Unit tests for the Debugger CLI commands."""

    def run_cli_command(self, command):
        """Helper to run CLI commands and return output."""
        result = subprocess.run(
            ["python", "debugger_cli.py"] + command,
            capture_output=True,
            text=True
        )
        return result.stdout.strip(), result.returncode

    def test_debug_command(self):
        """Test running the debugging process."""
        output, return_code = self.run_cli_command(["--debug"])
        self.assertIn("🚀 Starting Full Automated Debugging Process...", output)
        self.assertEqual(return_code, 0)

    def test_debug_specific_file(self):
        """Test debugging a specific file."""
        output, return_code = self.run_cli_command(["--debug", "--file", "sample_test.py"])
        self.assertIn("🚀 Debugging Specific File: sample_test.py...", output)
        self.assertEqual(return_code, 0)

    def test_logs_command(self):
        """Test retrieving previous debug logs."""
        output, return_code = self.run_cli_command(["--logs"])
        self.assertIn("📜 Retrieving Debug Logs...", output)
        self.assertEqual(return_code, 0)

    def test_rollback_command(self):
        """Test rolling back last attempted fixes."""
        output, return_code = self.run_cli_command(["--rollback"])
        self.assertIn("🔄 Rolling Back Last Attempted Fixes...", output)
        self.assertEqual(return_code, 0)

    def test_performance_command(self):
        """Test AI debugging performance report retrieval."""
        if not os.path.exists(AI_PERFORMANCE_FILE):
            # Create a dummy performance file for testing
            with open(AI_PERFORMANCE_FILE, "w", encoding="utf-8") as f:
                json.dump({"2025-02-14": {"total_fixes": 10, "success_rate": 90, "ai_feedback": [4.5, 4.7]}}, f)

        output, return_code = self.run_cli_command(["--performance"])
        self.assertIn("📈 **AI Debugging Performance Report** 📈", output)
        self.assertEqual(return_code, 0)

    def test_fix_imports_command(self):
        """Test the import fix tracking feature."""
        output, return_code = self.run_cli_command(["--fix-imports"])
        self.assertIn("🔍 Scanning for Import Errors...", output)
        self.assertEqual(return_code, 0)

    def tearDown(self):
        """Clean up test-generated files."""
        if os.path.exists(AI_PERFORMANCE_FILE):
            os.remove(AI_PERFORMANCE_FILE)


if __name__ == "__main__":
    unittest.main()
