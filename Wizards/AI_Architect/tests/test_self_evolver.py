import os
import unittest
import subprocess
import textwrap
from app.core.self_evolver import SelfEvolver


class TestSelfEvolver(unittest.TestCase):
    """
    Unit tests for the SelfEvolver module.
    """

    def setUp(self):
        """
        Set up a temporary test file with sample code that contains:
        - A long function that should be split.
        - A function missing a docstring.
        - An inefficient function with unused variables.
        """
        self.test_file_path = "./tests/test_code.py"
        os.makedirs(os.path.dirname(self.test_file_path), exist_ok=True)

        sample_code = textwrap.dedent("""
            def long_function():
                a = 10
                b = 20
                c = a + b
                d = a * b
                e = a / b
                f = a - b
                g = a ** b
                h = a % b
                i = a // b
                j = a & b
                k = a | b
                l = a ^ b
                m = a << b
                n = a >> b
                o = max(a, b)
                p = min(a, b)
                q = abs(a)
                r = round(a)
                s = divmod(a, b)
                t = pow(a, b)
                return c + d + e + f + g + h + i + j + k + l + m + n + o + p + q + r + s[0] + t

            def no_docstring():
                pass

            def inefficient_function():
                a = 10
                b = 20
                c = a + b
                unused_var = 100
                return c
        """).strip()

        with open(self.test_file_path, "w", encoding="utf-8") as file:
            file.write(sample_code)

    def tearDown(self):
        """
        Clean up the test file after each test run.
        """
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_analyze_code(self):
        """
        Test that SelfEvolver.analyze_code returns suggestions for improvements:
        - It should detect missing docstrings.
        - It should warn when functions are too long.
        """
        suggestions = SelfEvolver.analyze_code(self.test_file_path)

        self.assertIn("Function 'no_docstring' is missing a docstring.", suggestions)
        self.assertIn("Function 'long_function' is too long. Consider splitting it.", suggestions)

    def test_apply_improvements(self):
        """
        Test that SelfEvolver.apply_improvements applies the suggestions:
        - The function should insert TODO docstrings into functions missing documentation.
        """
        suggestions = SelfEvolver.analyze_code(self.test_file_path)
        SelfEvolver.apply_improvements(self.test_file_path, suggestions)

        with open(self.test_file_path, "r", encoding="utf-8") as file:
            content = file.read()

        self.assertIn('"""TODO: Add docstring for no_docstring."""', content)
        self.assertIn('"""TODO: Add docstring for long_function."""', content)


def get_ai_suggestions(code: str):
    """
    Sends Python code to Mistral via Ollama for AI-driven code analysis.

    Args:
        code (str): The Python code to analyze.

    Returns:
        list: A list of suggestion strings provided by the AI, split by lines.
    """
    prompt = (
        f"Analyze this Python code and suggest improvements. "
        f"Focus on detecting unused variables, inefficient logic, and possible optimizations:\n\n{code}"
    )

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",   # Ensure proper handling of special characters
            errors="replace"    # Replace problematic characters to avoid decoding errors
        )
        ai_response = result.stdout.strip()
        return ai_response.splitlines()  # Split the response into individual suggestions.
    except Exception as e:
        return [f"Error running Mistral analysis: {e}"]


if __name__ == "__main__":
    unittest.main()
