import unittest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True
    REDIS_URL = 'redis://localhost:6379/1' # Use a different DB for tests

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.app_context.pop()

    def test_main_page(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
