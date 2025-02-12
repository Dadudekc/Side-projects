import os
import unittest
from app.core.self_evolver import SelfEvolver

class TestSelfEvolver(unittest.TestCase):
    
    def setUp(self):
        # Create the necessary directories and the test file
        self.test_file_path = "./tests/test_code.py"
        
        # Ensure the 'tests' directory exists
        os.makedirs(os.path.dirname(self.test_file_path), exist_ok=True)

        with open(self.test_file_path, "w") as file:
            file.write("""
def long_function():
    a = 10
    b = 20
    c = a + b
    d = a * b
    e = a / b
    return c + d + e

def no_docstring():
    pass
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

if __name__ == "__main__":
    unittest.main()
