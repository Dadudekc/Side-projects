import unittest
from unittest.mock import MagicMock
from ai_engine.models.debugger.auto_fix_manager import AutoFixManager

class TestAutoFixManager(unittest.TestCase):
    def setUp(self):
        self.manager = AutoFixManager()

    def test_apply_fix(self):
        self.manager.debugging_strategy = MagicMock()
        self.manager.apply_fix("test_patch")
        self.manager.debugging_strategy.apply_patch.assert_called_once_with("test_patch")
