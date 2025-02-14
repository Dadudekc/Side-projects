import unittest
from agents.core.DebuggerAgent import DebuggerAgent

class TestDebuggerAgent(unittest.TestCase):
    """Unit tests for DebuggerAgent."""

    def setUp(self):
        """Initialize the DebuggerAgent before each test."""
        self.debugger = DebuggerAgent()

    def test_analyze_error(self):
        """Test analyzing an error message."""
        error_msg = "ModuleNotFoundError: No module named 'agents.core'"
        result = self.debugger.analyze_error(error=error_msg)
        self.assertIn("Error analysis result", result)

    def test_analyze_error_no_message(self):
        """Test analyzing an error when no message is provided."""
        result = self.debugger.analyze_error()
        self.assertEqual(result, "No error message provided for analysis.")

    def test_run_diagnostics(self):
        """Test running basic diagnostics."""
        result = self.debugger.run_diagnostics(system_check=True, detailed=False)
        self.assertIn("Basic diagnostics completed", result)

    def test_run_diagnostics_detailed(self):
        """Test running detailed diagnostics."""
        result = self.debugger.run_diagnostics(system_check=True, detailed=True)
        self.assertIn("Detailed report", result)

    def test_capabilities(self):
        """Test the capabilities description."""
        result = self.debugger.describe_capabilities()
        self.assertIn("can perform error analysis", result)

if __name__ == "__main__":
    unittest.main()
