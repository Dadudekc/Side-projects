import unittest

def run_tests(test_class):
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    class DummyTest(unittest.TestCase):
        def test_dummy(self):
            self.assertTrue(True)

    run_tests(DummyTest)
