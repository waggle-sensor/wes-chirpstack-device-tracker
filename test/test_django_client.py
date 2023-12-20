import unittest
from unittest.mock import Mock, patch, MagicMock
from app.django_client import DjangoClient

DEV_EUI = 123456789
DJANGO_API_INTERFACE = "https://auth.sagecontinuum.org"
LC_ROUTER = "lorawanconnections/"
LK_ROUTER = "lorawankeys/"
LD_ROUTER = "lorawandevices/"
SH_ROUTER = "sensorhardwares/"
HW_MODEL = "sfmx100"
VSN = "W030"
NODE_TOKEN = "999294cef6fc3a95fe14c145612825ef5ae27567"

class TestDjangoClient(unittest.TestCase):
    def setUp(self):
        # Set up the DjangoClient with a mock args object
        self.args = Mock(
            django_api_interface=DJANGO_API_INTERFACE,
            lorawanconnection_router=LC_ROUTER,
            lorawankey_router=LK_ROUTER,
            lorawandevice_router=LD_ROUTER,
            sensorhardware_router=SH_ROUTER,
            vsn=VSN,
            node_token=NODE_TOKEN
        )
        self.django_client = DjangoClient(self.args)

    @patch("app.django_client.HttpMethod.GET")
    def test_get_lc(self, mock_get):
        """
        Mocks the requests.get method in django client's get_lc method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 1, 
            'node': 'W030', 
            'lorawan_device': '123456789', 
            'connection_name': 'test', 
            'created_at': '2023-11-03T20:49:56.290798Z', 
            'last_seen_at': '2023-11-03T20:49:42Z', 
            'margin': '25.00', 
            'expected_uplink_interval_sec': 1, 
            'connection_type': 'OTAA'
        }
        mock_get.return_value = mock_response

        # Call the method under test
        result = self.django_client.get_lc(dev_eui=DEV_EUI)

        # Assertions
        mock_get.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawanconnections/{VSN}/{DEV_EUI}/", headers=self.django_client.auth_header)
        self.assertEqual(result, {'id': 1, 'node': 'W030', 'lorawan_device': '123456789', 
        'connection_name': 'test', 'created_at': '2023-11-03T20:49:56.290798Z', 
        'last_seen_at': '2023-11-03T20:49:42Z', 'margin': '25.00', 
        'expected_uplink_interval_sec': 1, 'connection_type': 'OTAA'})

    @patch("app.django_client.HttpMethod.POST")
    def test_create_lc(self, mock_post):
        """
        Mocks the requests.post method in django client's create_lc method to test it
        """
        create_data = {
            "node": "W030",
            "lorawan_device": "5556677",
            "connection_name": "MyConnection",
            "margin": 3.14,
            "expected_uplink_interval_sec": 60,
            "connection_type": "OTAA"
        }
        mock_response = Mock()
        mock_response.json.return_value = create_data
        mock_post.return_value = mock_response

        # Call the method under test
        result = self.django_client.create_lc(data=create_data)

        # Assertions
        mock_post.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawanconnections/", headers=self.django_client.auth_header, json=create_data)
        self.assertEqual(result, create_data)

    @patch("app.django_client.HttpMethod.PATCH")
    def test_update_lc(self, mock_patch):
        """
        Mocks the requests.patch method in django client's update_lc method to test it
        """
        data = {
            "node": "W030",
            "lorawan_device": "5556677",
            "connection_name": "MyConnection",
            "margin": 3.14,
            "expected_uplink_interval_sec": 60,
            "connection_type": "OTAA"
        }
        mock_response = Mock()
        mock_response.json.return_value = data
        mock_patch.return_value = mock_response

        # Call the method under test
        result = self.django_client.update_lc(dev_eui=DEV_EUI, data=data)

        # Assertions
        mock_patch.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawanconnections/{VSN}/{DEV_EUI}/", headers=self.django_client.auth_header, json=data)
        self.assertEqual(result, data)

    @patch("app.django_client.HttpMethod.GET")
    def test_get_ld(self, mock_get):
        """
        Mocks the requests.get method in django client's get_ld method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {"deveui":"123456789","device_name":"test","battery_level":"0.01"}
        mock_get.return_value = mock_response

        # Call the method under test
        result = self.django_client.get_ld(dev_eui=DEV_EUI)

        # Assertions
        mock_get.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawandevices/{DEV_EUI}/", headers=self.django_client.auth_header)
        self.assertEqual(result, {"deveui":"123456789","device_name":"test","battery_level":"0.01"})

    @patch("app.django_client.HttpMethod.POST")
    def test_create_ld(self, mock_post):
        """
        Mocks the requests.post method in django client's create_ld method to test it
        """
        create_data = {
            "deveui": "5556677",
            "device_name": "MyDevice",
            "battery_level": 5.1
        }
        mock_response = Mock()
        mock_response.json.return_value = create_data
        mock_post.return_value = mock_response

        # Call the method under test
        result = self.django_client.create_ld(data=create_data)

        # Assertions
        mock_post.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawandevices/", headers=self.django_client.auth_header, json=create_data)
        self.assertEqual(result, create_data)

    @patch("app.django_client.HttpMethod.PATCH")
    def test_update_ld(self, mock_patch):
        """
        Mocks the requests.patch method in django client's update_ld method to test it
        """
        data = {
            "deveui": "5556677",
            "device_name": "MyDevice",
            "battery_level": 5.1
        }
        mock_response = Mock()
        mock_response.json.return_value = data
        mock_patch.return_value = mock_response

        # Call the method under test
        result = self.django_client.update_ld(dev_eui=DEV_EUI, data=data)

        # Assertions
        mock_patch.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawandevices/{DEV_EUI}/", headers=self.django_client.auth_header, json=data)
        self.assertEqual(result, data)

    @patch("app.django_client.HttpMethod.GET")
    def test_get_lk(self, mock_get):
        """
        Mocks the requests.get method in django client's get_lk method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {
            "id":9,
            "lorawan_connection":"W030-test-123456789",
            "app_key":"12345", 
            "network_Key":"12345",
            "app_session_key":"12345",
            "dev_address":"12345"
        }
        mock_get.return_value = mock_response

        # Call the method under test
        result = self.django_client.get_lk(dev_eui=DEV_EUI)

        # Assertions
        mock_get.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawankeys/{VSN}/{DEV_EUI}/", headers=self.django_client.auth_header)
        self.assertEqual(result, {"id":9,"lorawan_connection":"W030-test-123456789","app_key":"12345", 
        "network_Key":"12345","app_session_key":"12345","dev_address":"12345"})

    @patch("app.django_client.HttpMethod.POST")
    def test_create_lk(self, mock_post):
        """
        Mocks the requests.post method in django client's create_lk method to test it
        """
        create_data = {        
            "lorawan_connection": "W030-test-123456789", 
            "app_key": "12345",         
            "network_Key": "12345",           
            "app_session_key": "12345",
            "dev_address": "12345"             
        }
        mock_response = Mock()
        mock_response.json.return_value = create_data
        mock_post.return_value = mock_response

        # Call the method under test
        result = self.django_client.create_lk(data=create_data)

        # Assertions
        mock_post.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawankeys/", headers=self.django_client.auth_header, json=create_data)
        self.assertEqual(result, create_data)

    @patch("app.django_client.HttpMethod.PATCH")
    def test_update_lk(self, mock_patch):
        """
        Mocks the requests.patch method in django client's update_lk method to test it
        """
        data = {        
            "lorawan_connection": "W030-test-123456789", 
            "app_key": "12345",         
            "network_Key": "12345",           
            "app_session_key": "12345",
            "dev_address": "12345"             
        }
        mock_response = Mock()
        mock_response.json.return_value = data
        mock_patch.return_value = mock_response

        # Call the method under test
        result = self.django_client.update_lk(dev_eui=DEV_EUI, data=data)

        # Assertions
        mock_patch.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawankeys/{VSN}/{DEV_EUI}/", headers=self.django_client.auth_header, json=data)
        self.assertEqual(result, data)

    @patch("app.django_client.HttpMethod.GET")
    def test_get_sh(self, mock_get):
        """
        Mocks the requests.get method in django client's get_sh method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {"hardware": "test","hw_model": HW_MODEL, "description": "test"}
        mock_get.return_value = mock_response

        # Call the method under test
        result = self.django_client.get_sh(hw_model=HW_MODEL)

        # Assertions
        mock_get.assert_called_once_with(f"{DJANGO_API_INTERFACE}/sensorhardwares/{HW_MODEL}/", headers=self.django_client.auth_header)
        self.assertEqual(result, {"hardware": "test","hw_model": HW_MODEL, "description": "test"})

    @patch("app.django_client.HttpMethod.POST")
    def test_create_sh(self, mock_post):
        """
        Mocks the requests.post method in django client's create_sh method to test it
        """
        create_data = {"hardware": "test","hw_model": HW_MODEL, "description": "test"}
        mock_response = Mock()
        mock_response.json.return_value = create_data
        mock_post.return_value = mock_response

        # Call the method under test
        result = self.django_client.create_sh(data=create_data)

        # Assertions
        mock_post.assert_called_once_with(f"{DJANGO_API_INTERFACE}/sensorhardwares/", headers=self.django_client.auth_header, json=create_data)
        self.assertEqual(result, create_data)

    @patch("app.django_client.HttpMethod.PATCH")
    def test_update_sh(self, mock_patch):
        """
        Mocks the requests.patch method in django client's update_sh method to test it
        """
        data = {"hardware": "test","hw_model": HW_MODEL, "description": "test"}
        mock_response = Mock()
        mock_response.json.return_value = data
        mock_patch.return_value = mock_response

        # Call the method under test
        result = self.django_client.update_sh(hw_model=HW_MODEL, data=data)

        # Assertions
        mock_patch.assert_called_once_with(f"{DJANGO_API_INTERFACE}/sensorhardwares/{HW_MODEL}/", headers=self.django_client.auth_header, json=data)
        self.assertEqual(result, {"hardware": "test","hw_model": HW_MODEL, "description": "test"})

if __name__ == "__main__":
    unittest.main()
