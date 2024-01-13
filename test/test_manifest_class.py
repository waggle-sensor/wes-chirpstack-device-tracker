import unittest
from app.manifest import Manifest
import json
from unittest.mock import (
    Mock, 
    patch, 
    MagicMock, 
    mock_open, 
    call
)

MANIFEST_FILEPATH = '/etc/waggle/node-manifest-v2.json'

class TestlLoadManifest(unittest.TestCase):
    @patch('builtins.open', mock_open(read_data='{"key": "value"}'))
    def test_load_manifest_existing_file(self):
        """
        Tests the case when the file exists and json.load successfully loads the content.
        """
        # Arrange
        filepath = MANIFEST_FILEPATH
        manifest = Manifest(filepath)

        # Call the method under test
        result = manifest.load_manifest()

        # Assert
        self.assertEqual(result, {"key": "value"})

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_manifest_missing_file(self, mock_open_file):
        """
        Tests the case when the file is not found, and the method returns an empty dictionary.
        """
        # Arrange
        filepath = 'nonexistent_manifest'
        manifest = Manifest(filepath)

        # Call the method under test
        result = manifest.load_manifest()

        # Assert
        self.assertEqual(result, {})

class TestSaveManifest(unittest.TestCase):
    def setUp(self):
        self.filepath = MANIFEST_FILEPATH
        self.manifest = Manifest(self.filepath)

    @patch('app.manifest.tempfile.NamedTemporaryFile')
    @patch('app.manifest.os.replace')
    @patch('app.manifest.os.unlink')
    def test_save_manifest_happy_path(self, mock_os_unlink, mock_os_replace, mock_named_tempfile):
        """
        Test saving the manifest file successfully
        """
        # Arrange
        expected_json_content = {"key": "value"}
        self.manifest.dict = expected_json_content

        # Mocking
        with patch("app.manifest.logging.error") as mock_logging_error:
            
            # Call the method under test
            self.manifest.save_manifest()

            # Assert
            mock_os_replace.assert_called_once_with(mock_named_tempfile.return_value.name, self.filepath)
            mock_os_unlink.assert_called_once_with(mock_named_tempfile.return_value.name)
            mock_logging_error.assert_not_called()

if __name__ == '__main__':
    unittest.main()