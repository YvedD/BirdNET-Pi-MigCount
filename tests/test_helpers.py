import unittest
from scripts.utils.helpers import PHPConfigParser


class TestPHPConfigParser(unittest.TestCase):

    def test_get_with_string_fallback(self):
        """Test that PHPConfigParser handles string fallback values correctly"""
        parser = PHPConfigParser()
        parser.read_string("[section]\nkey=value")
        # Test with string fallback for missing key
        result = parser.get('section', 'missing_key', fallback='default')
        self.assertEqual(result, 'default')

    def test_get_with_numeric_fallback(self):
        """Test that PHPConfigParser handles numeric fallback values correctly"""
        parser = PHPConfigParser()
        parser.read_string("[section]\nkey=value")
        # Test with float fallback for missing key
        result = parser.get('section', 'missing_key', fallback=0.0)
        self.assertEqual(result, 0.0)
        # Test with int fallback for missing key
        result = parser.get('section', 'missing_key', fallback=100)
        self.assertEqual(result, 100)

    def test_get_strips_quotes_from_string_values(self):
        """Test that PHPConfigParser strips quotes from string values"""
        parser = PHPConfigParser()
        parser.read_string('[section]\nkey="quoted_value"')
        result = parser.get('section', 'key')
        self.assertEqual(result, 'quoted_value')

    def test_get_handles_unquoted_string_values(self):
        """Test that PHPConfigParser handles unquoted string values"""
        parser = PHPConfigParser()
        parser.read_string('[section]\nkey=unquoted_value')
        result = parser.get('section', 'key')
        self.assertEqual(result, 'unquoted_value')

    def test_get_with_raw_mode(self):
        """Test that PHPConfigParser returns raw values when raw=True"""
        parser = PHPConfigParser()
        parser.read_string('[section]\nkey="quoted_value"')
        result = parser.get('section', 'key', raw=True)
        self.assertEqual(result, '"quoted_value"')


if __name__ == '__main__':
    unittest.main()
