import unittest
from adex.src.service.resources_manager import ResourceManager

class TestResourceManager(unittest.TestCase):
    def test_load_and_process_resources(self):
        resources = ResourceManager.load_and_process_resources()
        self.assertIsInstance(resources, dict)
        self.assertIn("notepad", resources)

if __name__ == "__main__":
    unittest.main()
