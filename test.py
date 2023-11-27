import unittest
from unittest.mock import Mock, patch
from app.django_client import DjangoClient

DEV_EUI = 123456789
DJANGO_API_INTERFACE = "http://127.0.0.1:8000"
VSN = "W030"
NODE_TOKEN = "8ce294ce5bf65c95f7e4c635605122ef5ae27826"

class TestDjangoClient(unittest.TestCase):
    def setUp(self):
        # Set up the DjangoClient with a mock args object
        self.args = Mock(django_api_interface=DJANGO_API_INTERFACE, vsn=VSN, node_token=NODE_TOKEN)
        self.django_client = DjangoClient(self.args)

    @patch("app.django_client.requests.get")
    def test_get_lc(self, mock_get):
        """
        Mock the requests.get method to return a response
        """
        mock_response = Mock()
        mock_response.json.return_value = {"example": "data"}
        mock_get.return_value = mock_response

        # Call the method under test
        result = self.django_client.get_lc(dev_eui=DEV_EUI)

        # Assertions
        mock_get.assert_called_once_with(f"{DJANGO_API_INTERFACE}/lorawanconnections/{VSN}/{DEV_EUI}/", headers=self.django_client.auth_header)
        self.assertEqual(result, {"example": "data"})

    @patch("app.django_client.requests.post")
    def test_create_lc(self, mock_post):
        """
        Mock the requests.post method to return a response
        """
        mock_response = Mock()
        mock_response.json.return_value = {"created": True}
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
        self.assertEqual(result, {"created": True})

if __name__ == "__main__":
    unittest.main()
