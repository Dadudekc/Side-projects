import unittest
from app.core.project_manager import ProjectManager

class TestProjectManager(unittest.TestCase):
    def test_get_project_name(self):
        manager = ProjectManager("Test Project")
        self.assertEqual(manager.get_project_name(), "Test Project")

if __name__ == "__main__":
    unittest.main()
