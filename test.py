import unittest
from unittest.mock import Mock, patch
from app.django_client import DjangoClient

DEV_EUI = 123456789
DJANGO_API_INTERFACE = "http://127.0.0.1:8000"
VSN = "W030"
NODE_TOKEN = "999294cef6fc3a95fe14c145612825ef5ae27567"

class TestDjangoClient(unittest.TestCase):
    def setUp(self):
        # Set up the DjangoClient with a mock args object
        self.args = Mock(django_api_interface=DJANGO_API_INTERFACE, vsn=VSN, node_token=NODE_TOKEN)
        self.django_client = DjangoClient(self.args)

    @patch("app.django_client.requests.get")
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

    @patch("app.django_client.requests.post")
    def test_create_lc(self, mock_post):
        """
        Mocks the requests.post method in django client's create_lc method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {'message': 'LorawanConnection created successfully'}
        mock_post.return_value = mock_response

        # Call the method under test
        create_data = {
            "node": "W030",
            "lorawan_device": "5556677",
            "connection_name": "MyConnection",
            "margin": 3.14,
            "expected_uplink_interval_sec": 60,
            "connection_type": "OTAA"
        }
        result = self.django_client.create_lc(data=create_data)

        # Assertions
        mock_post.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawanconnections/create/", headers=self.django_client.auth_header, json=create_data)
        self.assertEqual(result, {'message': 'LorawanConnection created successfully'})

    @patch("app.django_client.requests.patch")
    def test_update_lc(self, mock_patch):
        """
        Mocks the requests.patch method in django client's update_lc method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {"message":"LorawanConnection updated successfully"}
        mock_patch.return_value = mock_response

        # Call the method under test
        data = { "margin": "25"}
        result = self.django_client.update_lc(dev_eui=DEV_EUI, data=data)

        # Assertions
        mock_patch.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawanconnections/update/{VSN}/{DEV_EUI}/", headers=self.django_client.auth_header, json=data)
        self.assertEqual(result, {"message":"LorawanConnection updated successfully"})

    @patch("app.django_client.requests.get")
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

    @patch("app.django_client.requests.post")
    def test_create_ld(self, mock_post):
        """
        Mocks the requests.post method in django client's create_ld method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {"message": "LorawanDevice created successfully"}
        mock_post.return_value = mock_response

        # Call the method under test
        create_data = {
            "deveui": "5556677",
            "device_name": "MyDevice",
            "battery_level": 5.1
        }
        result = self.django_client.create_ld(data=create_data)

        # Assertions
        mock_post.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawandevices/create/", headers=self.django_client.auth_header, json=create_data)
        self.assertEqual(result, {"message": "LorawanDevice created successfully"})

    @patch("app.django_client.requests.patch")
    def test_update_ld(self, mock_patch):
        """
        Mocks the requests.patch method in django client's update_ld method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {"message": "LorawanDevice updated successfully"}
        mock_patch.return_value = mock_response

        # Call the method under test
        data = { "battery_level": 3.1}
        result = self.django_client.update_ld(dev_eui=DEV_EUI, data=data)

        # Assertions
        mock_patch.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawandevices/update/{DEV_EUI}/", headers=self.django_client.auth_header, json=data)
        self.assertEqual(result, {"message": "LorawanDevice updated successfully"})

    @patch("app.django_client.requests.get")
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

    @patch("app.django_client.requests.post")
    def test_create_lk(self, mock_post):
        """
        Mocks the requests.post method in django client's create_lk method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {"message": "Lorawan Key created successfully"}
        mock_post.return_value = mock_response

        # Call the method under test
        create_data = {        
            "lorawan_connection": "W030-test-123456789", 
            "app_key": "12345",         
            "network_Key": "12345",           
            "app_session_key": "12345",
            "dev_address": "12345"             
        }
        result = self.django_client.create_lk(data=create_data)

        # Assertions
        mock_post.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawankeys/create/", headers=self.django_client.auth_header, json=create_data)
        self.assertEqual(result, {"message": "Lorawan Key created successfully"})

    @patch("app.django_client.requests.patch")
    def test_update_lk(self, mock_patch):
        """
        Mocks the requests.patch method in django client's update_lk method to test it
        """
        mock_response = Mock()
        mock_response.json.return_value = {"message": "LorawanKey updated successfully"}
        mock_patch.return_value = mock_response

        # Call the method under test
        data = { "app_key": "1556"}
        result = self.django_client.update_lk(dev_eui=DEV_EUI, data=data)

        # Assertions
        mock_patch.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawankeys/update/{VSN}/{DEV_EUI}/", headers=self.django_client.auth_header, json=data)
        self.assertEqual(result, {"message": "LorawanKey updated successfully"})

if __name__ == "__main__":
    unittest.main()
