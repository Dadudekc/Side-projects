import unittest
from unittest.mock import MagicMock, patch

from agents.core.utilities.ai_model_manager import AIModelManager
from agents.core.AgentBase import AgentBase
from agents.core.utilities.debug_agent_utils import DebugAgentUtils
from ai_engine.models.debugger.debugger_core import DebugAgent


class TestDebuggerAgent(unittest.TestCase):
    """Unit tests for DebugAgent."""

    def setUp(self):
        """Initialize the DebugAgent before each test."""
        self.agent = DebugAgent()

    @patch("subprocess.run")
    def test_run_tests(self, mock_subprocess):
        """Test running tests with pytest."""
        mock_subprocess.return_value = MagicMock(stdout="Test Passed", stderr="")
        result = self.agent.run_tests()
        self.assertIn("Test Passed", result)

    def test_parse_test_failures(self):
        """Test parsing test failures from pytest output."""
        test_output = "FAILED test_file.py::test_example - AssertionError"
        failures = self.agent.parse_test_failures(test_output)

        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0]["file"], "test_file.py")
        self.assertEqual(failures[0]["test"], "test_example")
        self.assertEqual(failures[0]["error"], "AssertionError")

    @patch("agents.core.utilities.debug_agent_utils.DebugAgentUtils.apply_diff_patch")
    def test_apply_fix(self, mock_apply_patch):
        """Test applying a fix to a failing test."""
        mock_apply_patch.return_value = True
        failure = {
            "file": "test_file.py",
            "test": "test_example",
            "error": "SyntaxError",
        }
        result = self.agent.apply_fix(failure)
        self.assertTrue(result)

    @patch("agents.core.debugger_agent.DebugAgent.run_tests")
    @patch("agents.core.debugger_agent.DebugAgent.parse_test_failures", return_value=[])
    def test_retry_tests_success(self, mock_parse_failures, mock_run_tests):
        """Test retrying tests and succeeding."""
        result = self.agent.retry_tests()
        self.assertEqual(result["status"], "success")

    @patch("agents.core.debugger_agent.DebugAgent.run_tests")
    @patch(
        "agents.core.debugger_agent.DebugAgent.parse_test_failures",
        return_value=[
            {"file": "test_file.py", "test": "test_example", "error": "SyntaxError"}
        ],
    )
    def test_retry_tests_failure(self, mock_parse_failures, mock_run_tests):
        """Test retrying tests and failing."""
        result = self.agent.retry_tests(max_retries=1)
        self.assertEqual(result["status"], "error")

    def test_analyze_error(self):
        """Test analyzing an error message."""
        result = self.agent.analyze_error("SyntaxError: unexpected EOF")
        self.assertIn("Error analysis result", result)

    def test_analyze_error_no_message(self):
        """Test analyzing an error when no message is provided."""
        result = self.agent.analyze_error("")
        self.assertEqual(result, "No error message provided for analysis.")

    def test_run_diagnostics(self):
        """Test running basic diagnostics."""
        result = self.agent.run_diagnostics(system_check=True, detailed=False)
        self.assertIn("Basic diagnostics completed", result)

    def test_run_diagnostics_detailed(self):
        """Test running detailed diagnostics."""
        result = self.agent.run_diagnostics(system_check=True, detailed=True)
        self.assertIn("Detailed report", result)

    def test_capabilities(self):
        """Test the capabilities description."""
        result = self.agent.describe_capabilities()
        self.assertIn("can perform error analysis", result)


if __name__ == "__main__":
    unittest.main()