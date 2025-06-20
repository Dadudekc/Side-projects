import os
import sys
import unittest

# Ensure the parent directory is in sys.path for import
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api_wizard import APIWizard

class TestAPIWizard(unittest.TestCase):
    def test_get_api_name(self):
        wizard = APIWizard("Sample API")
        self.assertEqual(wizard.get_api_name(), "Sample API")

if __name__ == "__main__":
    unittest.main()
