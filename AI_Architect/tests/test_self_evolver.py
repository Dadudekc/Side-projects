import os
import unittest
from unittest.mock import patch
from app.core.self_evolver import SelfEvolver

class TestSelfEvolver(unittest.TestCase):
    
    def setUp(self):
        # Create the necessary directories and the test file
        self.test_file_path = "./tests/test_code.py"
        os.makedirs(os.path.dirname(self.test_file_path), exist_ok=True)

        # Test file with both long functions and inefficient code
        with open(self.test_file_path, "w") as file:
            file.write("""
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
            """)

    def tearDown(self):
        # Remove the temporary test file after each test
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def test_analyze_code(self):
        suggestions = SelfEvolver.analyze_code(self.test_file_path)
        
        # Check that suggestions were generated for missing docstrings and long function
        self.assertIn("Function 'no_docstring' is missing a docstring.", suggestions)
        self.assertIn("Function 'long_function' is too long. Consider splitting it.", suggestions)
    
    def test_apply_improvements(self):
        suggestions = SelfEvolver.analyze_code(self.test_file_path)
        
        # Apply improvements based on suggestions
        result = SelfEvolver.apply_improvements(self.test_file_path, suggestions)
        
        # Verify that improvements were applied (i.e., docstring added)
        with open(self.test_file_path, "r") as file:
            content = file.read()
        
        self.assertIn('"""TODO: Add docstring for no_docstring."""', content)
        self.assertIn('"""TODO: Add docstring for long_function."""', content)

    @staticmethod
    def get_ai_suggestions(code: str):
        """
        Sends code to Mistral via ollama for AI-driven code analysis.
        """
        prompt = f"Analyze this Python code and suggest improvements. Focus on detecting unused variables, inefficient logic, and possible optimizations:\n\n{code}"
        
        try:
            # Run Mistral via Ollama with UTF-8 decoding
            result = subprocess.run(
                ["ollama", "run", "mistral", prompt],
                capture_output=True,
                text=True,
                encoding='utf-8'  # Force UTF-8 to handle special characters
            )
            
            # Process the AI suggestions
            ai_response = result.stdout.strip()
            return ai_response.split('\n')  # Assuming suggestions are separated by newlines
        
        except Exception as e:
            return [f"Error running Mistral analysis: {e}"]


if __name__ == "__main__":
    unittest.main()
