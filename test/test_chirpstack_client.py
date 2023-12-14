import unittest
from unittest.mock import Mock, patch, MagicMock
from app.chirpstack_client import ChirpstackClient
import grpc
from grpc import _channel as channel
from chirpstack_api import api
import sys

CHIRPSTACK_API_INTERFACE = "wes-chirpstack-server:8080"
CHIRPSTACK_ACT_EMAIL = "test"
CHIRPSTACK_ACT_PASSWORD = "test"

#TODO: Use sample data instead of mocking, maybe use factories lib (look at line of code with `Example` tag)

class TestLogin(unittest.TestCase):

    @patch('app.chirpstack_client.grpc.insecure_channel')
    @patch('app.chirpstack_client.api.InternalServiceStub')
    def test_login_success(self, mock_internal_service_stub, mock_insecure_channel):
        """
        Test a succesful pass through of login
        """
        args = MagicMock()
        args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD

        # Mocking grpc login response
        mock_login_response = MagicMock(jwt='mock_jwt_token')
        mock_internal_service_stub.return_value.Login.return_value = mock_login_response

        # Creating ChirpstackClient instance
        client = ChirpstackClient(args)

        # Assert that the login method was called with the correct parameters
        mock_internal_service_stub.return_value.Login.assert_called_once_with(
            api.LoginRequest(email=args.chirpstack_account_email, password=args.chirpstack_account_password)
        )

        # Assert that the auth_token is set correctly
        self.assertEqual(client.auth_token, 'mock_jwt_token')

    @patch('app.chirpstack_client.grpc.insecure_channel')
    @patch('app.chirpstack_client.api.InternalServiceStub')
    def test_login_failure_InactiveRpcError_grpcStatusCodeUNAUTHENTICATED(self, mock_internal_service_stub, mock_insecure_channel):
        """
        Test the login method with a InactiveRpcError exception with a grpc.StatusCode.UNAUTHENTICATED
        """
        args = MagicMock()
        args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        args.chirpstack_account_password = 'wrong_password'

        # Mocking grpc login response
        mock_internal_service_stub.return_value.Login.side_effect = channel._InactiveRpcError(
            MagicMock(code=lambda: grpc.StatusCode.UNAUTHENTICATED, details=lambda: 'Invalid credentials')
        )

        # Creating ChirpstackClient instance
        with self.assertRaises(SystemExit) as cm:
            ChirpstackClient(args)

        # Assert that the system exit code is 1 (indicating failure)
        self.assertEqual(cm.exception.code, 1)

    @patch('app.chirpstack_client.grpc.insecure_channel')
    @patch('app.chirpstack_client.api.InternalServiceStub')
    def test_login_failure_Exception(self, mock_internal_service_stub, mock_insecure_channel):
        """
        Test the login method with a general exception
        """
        args = MagicMock()
        args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD

        # Mocking grpc login response to raise a general Exception
        mock_internal_service_stub.return_value.Login.side_effect = Exception("Test exception")

        # Creating ChirpstackClient instance
        with self.assertRaises(SystemExit) as cm:
            ChirpstackClient(args)

        # Assert that the system exit code is 1 (indicating failure)
        self.assertEqual(cm.exception.code, 1)

class TestListAllDevices(unittest.TestCase):

    def setUp(self):
        # Mock the arguments
        self.mock_args = Mock()
        self.mock_args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        self.mock_args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        self.mock_args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD

    @patch('app.chirpstack_client.api.InternalServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_list_all_devices_happy_path(self, mock_insecure_channel, mock_internal_service_stub):
        """
        Test list_all_devices() method's happy path by mocking list_all_apps() reponse and List_agg_pagination()
        """

        # Mock List_agg_pagination
        mock_list_agg_pagination = Mock(return_value=["device1", "device2"]) #Example

        with patch.object(ChirpstackClient, 'List_agg_pagination', mock_list_agg_pagination):
            # Create a ChirpstackClient instance
            client = ChirpstackClient(self.mock_args)

            # Mock the app_resp for list_all_apps
            mock_app_resp = [Mock(id="app1"), Mock(id="app2")] #Example

            # Call list_all_devices
            devices = client.list_all_devices(mock_app_resp)

            # Assert the result
            self.assertEqual(devices, ['device1', 'device2', 'device1', 'device2'])

class TestListAllApps(unittest.TestCase):
    def setUp(self):
        # Mock the arguments
        self.mock_args = Mock()
        self.mock_args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        self.mock_args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        self.mock_args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD

    @patch('app.chirpstack_client.api.InternalServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_list_all_apps_happy_path(self, mock_insecure_channel, mock_internal_service_stub):
        """
        Test list_all_apps() method's happy path by mocking list_tenants() reponse and List_agg_pagination()
        """

        # Mock List_agg_pagination
        mock_list_agg_pagination = Mock(return_value=["app1", "app2"]) 

        with patch.object(ChirpstackClient, 'List_agg_pagination', mock_list_agg_pagination):
            # Create a ChirpstackClient instance
            client = ChirpstackClient(self.mock_args)

            # Mock the tenant_resp for list_all_devices
            mock_tenant_resp = [Mock(id="tenant1"), Mock(id="tenant2")]

            # Call list_all_devices
            apps = client.list_all_apps(mock_tenant_resp)

            # Assert the result
            self.assertEqual(apps, ['app1', 'app2', 'app1', 'app2'])

class TestListTenants(unittest.TestCase):
    def setUp(self):
        # Mock the arguments
        self.mock_args = Mock()
        self.mock_args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        self.mock_args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        self.mock_args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD

    @patch('app.chirpstack_client.api.InternalServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_list_all_apps_happy_path(self, mock_insecure_channel, mock_internal_service_stub):
        """
        Test list_tenants() method's happy path by mocking List_agg_pagination()
        """

        # Mock List_agg_pagination
        mock_list_agg_pagination = Mock(return_value=["Tenant1", "Tenant1"]) 

        with patch.object(ChirpstackClient, 'List_agg_pagination', mock_list_agg_pagination):
            # Create a ChirpstackClient instance
            client = ChirpstackClient(self.mock_args)

            # Call list_tenants()
            tenants = client.list_tenants()

            # Assert the result
            self.assertEqual(tenants, ["Tenant1", "Tenant1"])

class TestGetDeviceProfile(unittest.TestCase):

    def setUp(self):
        # Mock the arguments
        self.mock_args = Mock()
        self.mock_args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        self.mock_args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        self.mock_args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD

    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_get_device_profile_happy_path(self, mock_insecure_channel, mock_device_profile_service_stub):
        """
        Test get_device_profile() method's happy path
        """
        # Mock the gRPC channel and login response
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceProfileServiceStub
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value
        mock_device_profile_service_stub_instance.Get.return_value = Mock(device_profile_info="mock_device_profile_info")

        # Create a ChirpstackClient instance
        client = ChirpstackClient(self.mock_args)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        device_profile_info = client.get_device_profile(mock_device_profile_id)

        # Assert the result
        self.assertEqual(device_profile_info.device_profile_info, "mock_device_profile_info")

class TestGetDeviceAppKey(unittest.TestCase):

    def setUp(self):
        # Mock the arguments
        self.mock_args = Mock()
        self.mock_args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        self.mock_args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        self.mock_args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD

    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_get_device_app_key_happy_path(self, mock_insecure_channel, mock_device_service_stub):
        """
        Test get_device_app_key() method's happy path
        """
        # Mock the gRPC channel and login response
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_service_stub_instance.GetKeys.return_value = Mock(device_keys=Mock(nwk_key="mock_app_key"))

        # Create a ChirpstackClient instance
        client = ChirpstackClient(self.mock_args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call get_device_app_key
        app_key = client.get_device_app_key(mock_dev_eui)

        # Assert the result
        self.assertEqual(app_key, "mock_app_key")

    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_get_device_app_key_failure_NOTFOUND(self, mock_insecure_channel, mock_device_service_stub):
        """
        Test the get_device_app_key() method with a InactiveRpcError exception with a grpc.StatusCode.NOT_FOUND
        """
        # Mock the gRPC channel and login response
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        # Mock the GetKeys method to raise grpc._channel._InactiveRpcError
        mock_device_service_stub_instance.GetKeys.side_effect = channel._InactiveRpcError(
            MagicMock(code=lambda: grpc.StatusCode.NOT_FOUND, details=lambda: 'Not found')
        )

        # Create a ChirpstackClient instance
        client = ChirpstackClient(self.mock_args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call get_device_app_key
        app_key = client.get_device_app_key(mock_dev_eui)

        # Assert the result
        self.assertIsNone(app_key)

    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_get_device_app_key_failure_Other(self, mock_insecure_channel, mock_device_service_stub):
        """
        Test the get_device_app_key() method with a InactiveRpcError exception thats other than a grpc.StatusCode.NOT_FOUND
        """
        # Mock the gRPC channel and login response
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        # Mock the GetKeys method to raise grpc._channel._InactiveRpcError
        mock_device_service_stub_instance.GetKeys.side_effect = channel._InactiveRpcError(
            MagicMock(code=lambda: grpc.StatusCode.UNAUTHENTICATED, details=lambda: 'Invalid credentials')
        )

        # Create a ChirpstackClient instance
        client = ChirpstackClient(self.mock_args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call get_device_app_key
        app_key = client.get_device_app_key(mock_dev_eui)

        # Assert the result
        self.assertIsNone(app_key)

    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_get_device_app_key_failure_Exception(self, mock_insecure_channel, mock_device_service_stub):
        """
        Test the get_device_app_key() method with a general exception
        """
        # Mock the gRPC channel and login response
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        # Mock the GetKeys method to raise grpc._channel._InactiveRpcError
        mock_device_service_stub_instance.GetKeys.side_effect = Exception("Test exception")

        # Create a ChirpstackClient instance
        client = ChirpstackClient(self.mock_args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call get_device_app_key
        app_key = client.get_device_app_key(mock_dev_eui)

        # Assert the result
        self.assertIsNone(app_key)

class TestGetDeviceActivation(unittest.TestCase):

    def setUp(self):
        # Mock the arguments
        self.mock_args = Mock()
        self.mock_args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        self.mock_args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        self.mock_args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD
    
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_get_device_activation_happy_path(self, mock_insecure_channel, mock_device_service_stub):
        """
        Test get_device_activation() method's happy path
        """
        # Mock the gRPC channel and login response
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_service_stub_instance.GetActivation.return_value = Mock(activation_details="mock_activation_details")

        # Create a ChirpstackClient instance
        client = ChirpstackClient(self.mock_args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call get_device_app_key
        response = client.get_device_activation(mock_dev_eui)

        # Assert the result
        self.assertEqual(response.activation_details, "mock_activation_details")

class TestListAggPagination(unittest.TestCase):

    def setUp(self):
        # Mock the arguments
        self.mock_args = Mock()
        self.mock_args.chirpstack_api_interface = CHIRPSTACK_API_INTERFACE
        self.mock_args.chirpstack_account_email = CHIRPSTACK_ACT_EMAIL
        self.mock_args.chirpstack_account_password = CHIRPSTACK_ACT_PASSWORD

    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_list_agg_pagination(self, mock_insecure_channel, mock_device_service_stub):
        """
        Test list_agg_pagination() method's happy path
        """
        # Mock the gRPC channel and login response
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_list_response = Mock(result=["result_page1", "result_page2"], total_count=2)
        mock_device_service_stub_instance.List.return_value = mock_list_response

        # Create a ChirpstackClient instance
        client = ChirpstackClient(self.mock_args)

        # Mock the request and metadata
        mock_req = Mock(offset=0,limit=1)
        mock_metadata = [("authorization", "Bearer mock_jwt")]

        # Call List_agg_pagination
        aggregated_records = ChirpstackClient.List_agg_pagination(mock_device_service_stub_instance, mock_req, mock_metadata)

        # Assert the result
        self.assertEqual(aggregated_records, ["result_page1", "result_page2"])

if __name__ == "__main__":
    unittest.main()