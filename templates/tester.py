import unittest
from unittest.mock import MagicMock
from connection_tester import initialize_database

class TestWebsiteChecker(unittest.TestCase):

    def setUp(self):
        # Set up any necessary resources or configurations for the tests
        pass

    def tearDown(self):
        # Clean up any resources after the tests
        pass

    def test_initialize_database(self):
        # Mock the sqlite3.connect method
        with unittest.mock.patch('sqlite3.connect') as mock_connect:
            # Create a mock cursor
            mock_cursor = MagicMock()

            # Set the return value of connect to the mock_cursor
            mock_connect.return_value.cursor.return_value = mock_cursor

            # Call the function to be tested
            initialize_database()

            # Assert that the creation method was called with the expected SQL query
            mock_cursor.execute.assert_called_with('''CREATE TABLE IF NOT EXISTS website_status (id INTEGER PRIMARY KEY AUTOINCREMENT,time TEXT,date TEXT,website TEXT,
                   availability_status TEXT,status_code INTEGER)''')


if __name__ == '__main__':
    unittest.main()
