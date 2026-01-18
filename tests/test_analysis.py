import os
import unittest
from unittest.mock import patch
from io import StringIO

from scripts.utils.analysis import run_analysis, _get_numeric_setting
from scripts.utils.classes import ParseFileName
from tests.helpers import TESTDATA, Settings
from scripts.utils.analysis import filter_humans
from scripts.utils.helpers import PHPConfigParser


class DummyConf:
    def __init__(self, value):
        self.value = value

    def get(self, key, fallback=None):
        if key == 'HIGHPASS_HZ':
            return self.value
        return fallback


class TestRunAnalysis(unittest.TestCase):

    def setUp(self):
        source = os.path.join(TESTDATA, 'Pica pica_30s.wav')
        self.test_file = os.path.join(TESTDATA, '2024-02-24-birdnet-16:19:37.wav')
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
        os.symlink(source, self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)

    @patch('scripts.utils.helpers._load_settings')
    @patch('scripts.utils.analysis.loadCustomSpeciesList')
    def test_run_analysis(self, mock_loadCustomSpeciesList, mock_load_settings):
        # Mock the settings and species list
        mock_load_settings.return_value = Settings.with_defaults()
        mock_loadCustomSpeciesList.return_value = []

        # Test file
        test_file = ParseFileName(self.test_file)

        # Expected results
        expected_results = [
            {"confidence": 0.912, 'sci_name': 'Pica pica'},
            {"confidence": 0.9316, 'sci_name': 'Pica pica'},
            {"confidence": 0.8857, 'sci_name': 'Pica pica'}
        ]

        # Run the analysis
        detections = run_analysis(test_file)

        # Assertions
        self.assertEqual(len(detections), len(expected_results))
        for det, expected in zip(detections, expected_results):
            self.assertAlmostEqual(det.confidence, expected['confidence'], delta=1e-4)
            self.assertEqual(det.scientific_name, expected['sci_name'])


class TestHighPassConfig(unittest.TestCase):

    def test_dict_conf_uses_default(self):
        conf = Settings.with_defaults()
        self.assertEqual(_get_numeric_setting(conf, 'HIGHPASS_HZ', 0.0), 0.0)

    def test_conf_with_fallback(self):
        self.assertEqual(_get_numeric_setting(DummyConf('150'), 'HIGHPASS_HZ', 0.0), 150.0)
        self.assertEqual(_get_numeric_setting(DummyConf('invalid'), 'HIGHPASS_HZ', 120.0), 120.0)


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


class TestFilterHumans(unittest.TestCase):

    @patch('scripts.utils.helpers._load_settings')
    def test_filter_humans_no_human(self, mock_load_settings):
        mock_load_settings.return_value = Settings.with_defaults()

        # Input detections without humans
        detections = [
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Bird_C', 0.7), ('Bird_D', 0.6)]
        ]

        # Expected output
        expected = [
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Bird_C', 0.7), ('Bird_D', 0.6)]
        ]

        # Run filter_humans
        result = filter_humans(detections)

        # Assertions
        self.assertEqual(result, expected)

    @patch('scripts.utils.helpers._load_settings')
    def test_filter_empty(self, mock_load_settings):
        mock_load_settings.return_value = Settings.with_defaults()

        # Input detections without humans
        detections = []

        # Expected output
        expected = []

        # Run filter_humans
        result = filter_humans(detections)

        # Assertions
        self.assertEqual(result, expected)

    @patch('scripts.utils.helpers._load_settings')
    def test_filter_humans_with_human(self, mock_load_settings):
        mock_load_settings.return_value = Settings.with_defaults()

        # Input detections with humans
        detections = [
            [('Human_Human', 0.95), ('Bird_A', 0.8)],
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Bird_C', 0.9), ('Bird_D', 0.8)],
            [('Bird_B', 0.7), ('Human vocal_Human vocal', 0.9)]
        ]

        # Expected output
        expected = [
            [('Human_Human', 0.0)],
            [('Human_Human', 0.0)],
            [('Human_Human', 0.0)],
            [('Human_Human', 0.0)]
        ]

        # Run filter_humans
        result = filter_humans(detections)

        # Assertions
        self.assertEqual(result, expected)

    @patch('scripts.utils.helpers._load_settings')
    def test_filter_humans_with_human_neighbour(self, mock_load_settings):
        mock_load_settings.return_value = Settings.with_defaults()

        # Input detections with human neighbours
        detections = [
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Bird_D', 0.9), ('Bird_E', 0.8)],
            [('Human_Human', 0.95), ('Bird_C', 0.7)],
            [('Bird_F', 0.6), ('Bird_G', 0.5)]
        ]

        # Expected output
        expected = [
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Human_Human', 0.0)],
            [('Human_Human', 0.0)],
            [('Human_Human', 0.0)]
        ]

        # Run filter_humans
        result = filter_humans(detections)

        # Assertions
        self.assertEqual(result, expected)

    @patch('scripts.utils.helpers._load_settings')
    def test_filter_humans_with_deep_human(self, mock_load_settings):
        mock_load_settings.return_value = Settings.with_defaults()

        # Input detections with human neighbours
        detections = [
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Bird_D', 0.9), ('Bird_E', 0.8)],
            [('Bird_C', 0.7)] * 10 + [('Human_Human', 0.95)],
            [('Bird_F', 0.6), ('Bird_G', 0.5)]
        ]

        # Expected output
        expected = [
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Bird_D', 0.9), ('Bird_E', 0.8)],
            [('Bird_C', 0.7)] * 10,
            [('Bird_F', 0.6), ('Bird_G', 0.5)]
        ]

        # Run filter_humans
        result = filter_humans(detections)

        # Assertions
        self.assertEqual(result, expected)

    @patch('scripts.utils.helpers._load_settings')
    def test_filter_humans_with_human_deep(self, mock_load_settings):
        settings = Settings.with_defaults()
        settings['PRIVACY_THRESHOLD'] = 1
        mock_load_settings.return_value = settings

        # Input detections with human neighbours
        detections = [
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Bird_D', 0.9), ('Bird_E', 0.8)],
            [('Bird_C', 0.7)] * 10 + [('Human_Human', 0.95)],
            [('Bird_F', 0.6), ('Bird_G', 0.5)]
        ]

        # Expected output
        expected = [
            [('Bird_A', 0.9), ('Bird_B', 0.8)],
            [('Human_Human', 0.0)],
            [('Human_Human', 0.0)],
            [('Human_Human', 0.0)]
        ]

        # Run filter_humans
        result = filter_humans(detections)

        # Assertions
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
