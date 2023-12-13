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

if __name__ == "__main__":
    unittest.main()