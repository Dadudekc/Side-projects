import unittest
from app.core.code_generator import generate_code

class TestCodeGenerator(unittest.TestCase):
    def test_generate_code(self):
        template = "def {function_name}():\n    return {return_value}"
        result = generate_code(template, function_name="hello", return_value="'world'")
        self.assertEqual(result, "def hello():\n    return 'world'")

if __name__ == "__main__":
    unittest.main()
