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

    @patch('app.manifest.tempfile.NamedTemporaryFile')
    @patch('app.manifest.os.replace')
    @patch('app.manifest.os.unlink')
    def test_save_manifest_exception_handling(self, mock_os_unlink, mock_os_replace, mock_named_tempfile):
        """
        Test the exception handling
        """
        # Arrange
        expected_json_content = {"key": "value"}
        self.manifest.dict = expected_json_content

        # Mocking
        with patch("app.manifest.logging.error") as mock_logging_error:
            
            # Simulate an exception during the save process
            mock_os_replace.side_effect = Exception("Simulated error")

            # Act
            self.manifest.save_manifest()

            # Assert
            mock_os_replace.assert_called_once_with(mock_named_tempfile.return_value.name, self.manifest.filepath)
            mock_os_unlink.assert_called_once_with(mock_named_tempfile.return_value.name)
            mock_logging_error.assert_called_once_with("Manifest.save_manifest(): Simulated error")

class TestLcCheck(unittest.TestCase):
    def setUp(self):
        self.filepath = MANIFEST_FILEPATH
        self.manifest = Manifest(self.filepath)

    def test_lc_check_found(self):
        """
        Test when lorawan connection is found
        """
        # Arrange
        json_content = {"lorawanconnections": []}
        self.manifest.dict = json_content

        self.assertTrue(self.manifest.lc_check())

    def test_lc_check_not_found(self):
        """
        Test when lorawan connection is not found
        """
        # Arrange
        json_content = {"key": "value"}
        self.manifest.dict = json_content

        self.assertFalse(self.manifest.lc_check())

class TestLdSearch(unittest.TestCase):
    def setUp(self):
        self.filepath = MANIFEST_FILEPATH
        self.manifest = Manifest(self.filepath)

    def test_ld_search_found(self):
        """
        Test when lorawan device is found
        """
        # Arrange
        deveui = "7d1f5420e81235c1"
        json_content = {"lorawanconnections": [{
            "connection_name": "SFM",
            "created_at": "2023-12-13T19:47:45.355000Z",
            "last_seen_at": "2023-12-13T19:47:45.355000Z",
            "margin": 5,
            "expected_uplink_interval_sec": 40,
            "connection_type": "OTAA",
            "lorawandevice": {
                "deveui": deveui,
                "name": "SFM1x Sap Flow",
                "battery_level": 10,
                "hardware": {
                    "hardware": "Sap Flow Meter",
                    "hw_model": "SFM1x",
                    "hw_version": "",
                    "sw_version": "",
                    "manufacturer": "ICT International",
                    "datasheet": "https://ictinternational.com/manuals-and-brochures/sfm1x-sap-flow-meter/",
                    "capabilities": [
                        "lorawan"
                    ],
                    "description": "# SFM1x Sap Flow Meter\r\n\r\nThe SFM1x Sap Flow Meter enables individual tree water use and health to be monitored in real time. This is because the SFM has integrated data transmission direct to cloud using IoT/LTE-M Cat-M1. The SFM1x Sap Flow Meter is a discrete standalone instrument based upon the Heat Ratio Method. This measurement principle has proven to be a robust and flexible technique to measure plant water use; being able to measure high, low, zero and reverse flows in a large range of plant anatomies & species from herbaceous to woody, and stem sizes > 10 mm in diameter. The theoretical basis and ratio metric design of the Heat Ratio Method makes possible the measurement of high, low, zero and reverse flows. The SFM1x Sap Flow Meter consists of two temperature sensing needles arranged equidistance above and below a central heater. These needles are inserted into the water conducting tissue of the plant by drilling 3 small parallel holes. Heat is then pulsed every 10 minutes into the water conducting tissue of the plant. The heat is used as a tracer to directly measure the velocity of water movement in the plant stem."
                }
            }
        }]}
        self.manifest.dict = json_content

        self.assertTrue(self.manifest.ld_search(deveui))

    def test_ld_search_not_found(self):
        """
        Test when lorawan device is not found
        """
        # Arrange
        deveui = "7d1f5420e81235c1"
        json_content = {"lorawanconnections": [{
            "connection_name": "SFM",
            "created_at": "2023-12-13T19:47:45.355000Z",
            "last_seen_at": "2023-12-13T19:47:45.355000Z",
            "margin": 5,
            "expected_uplink_interval_sec": 40,
            "connection_type": "OTAA",
            "lorawandevice": {
                "deveui": deveui,
                "name": "SFM1x Sap Flow",
                "battery_level": 10,
                "hardware": {
                    "hardware": "Sap Flow Meter",
                    "hw_model": "SFM1x",
                    "hw_version": "",
                    "sw_version": "",
                    "manufacturer": "ICT International",
                    "datasheet": "https://ictinternational.com/manuals-and-brochures/sfm1x-sap-flow-meter/",
                    "capabilities": [
                        "lorawan"
                    ],
                    "description": "# SFM1x Sap Flow Meter\r\n\r\nThe SFM1x Sap Flow Meter enables individual tree water use and health to be monitored in real time. This is because the SFM has integrated data transmission direct to cloud using IoT/LTE-M Cat-M1. The SFM1x Sap Flow Meter is a discrete standalone instrument based upon the Heat Ratio Method. This measurement principle has proven to be a robust and flexible technique to measure plant water use; being able to measure high, low, zero and reverse flows in a large range of plant anatomies & species from herbaceous to woody, and stem sizes > 10 mm in diameter. The theoretical basis and ratio metric design of the Heat Ratio Method makes possible the measurement of high, low, zero and reverse flows. The SFM1x Sap Flow Meter consists of two temperature sensing needles arranged equidistance above and below a central heater. These needles are inserted into the water conducting tissue of the plant by drilling 3 small parallel holes. Heat is then pulsed every 10 minutes into the water conducting tissue of the plant. The heat is used as a tracer to directly measure the velocity of water movement in the plant stem."
                }
            }
        }]}
        self.manifest.dict = json_content

        self.assertFalse(self.manifest.ld_search("123456789"))

    def test_ld_search_lc_found(self):
        """
        Test when lorawan connection array is not found
        """
        # Arrange
        deveui = "7d1f5420e81235c1"
        json_content = {"key": "value"}
        self.manifest.dict = json_content

        self.assertFalse(self.manifest.ld_search(deveui))

class TestIsValidJson(unittest.TestCase):
    def setUp(self):
        self.filepath = MANIFEST_FILEPATH
        self.manifest = Manifest(self.filepath)

    def test_is_valid_json_true(self):
        """
        Test when json is valid
        """
        # Arrange
        data = {"key": "value"}
        self.assertTrue(self.manifest.is_valid_json(data))

    def test_is_valid_json_false(self):
        """
        Test when json is not valid
        """
        # Arrange
        data = {'complex': 1 + 2j}
        self.assertFalse(self.manifest.is_valid_json(data))



if __name__ == '__main__':
    unittest.main()