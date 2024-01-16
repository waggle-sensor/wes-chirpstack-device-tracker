import unittest
from unittest.mock import Mock, patch, MagicMock
from app.chirpstack_client import ChirpstackClient
from app.django_client import DjangoClient, HttpMethod
from app.tracker import Tracker
from app.tracker.parse import *

API_INTERFACE = "https://auth.sagecontinuum.org"
LC_ROUTER = "lorawanconnections/"
LK_ROUTER = "lorawankeys/"
LD_ROUTER = "lorawandevices/"
SH_ROUTER = "sensorhardwares/"
VSN = "W030"
NODE_TOKEN = "999294cef6fc3a95fe14c145612825ef5ae27567"
CHIRPSTACK_API_INTERFACE = "wes-chirpstack-server:8080"
CHIRPSTACK_ACT_EMAIL = "test"
CHIRPSTACK_ACT_PASSWORD = "test"

class TestUpdateLd(unittest.TestCase):

    @patch('app.chirpstack_client.grpc.insecure_channel')
    def setUp(self, mock_insecure_channel):
        self.args = Mock(
            api_interface=API_INTERFACE,
            lorawanconnection_router=LC_ROUTER,
            lorawankey_router=LK_ROUTER,
            lorawandevice_router=LD_ROUTER,
            sensorhardware_router=SH_ROUTER,
            vsn=VSN,
            node_token=NODE_TOKEN,
            chirpstack_api_interface=CHIRPSTACK_API_INTERFACE,
            chirpstack_account_email=CHIRPSTACK_ACT_EMAIL,
            chirpstack_account_password=CHIRPSTACK_ACT_PASSWORD
        )

        #set up tracker
        self.tracker = Tracker(self.args)

    @patch("app.django_client.HttpMethod.PATCH")
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_update_ld_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_django_patch):
        """
        Successfully uses chirpstack lorawan device data to call django's client update_ld()
        """
        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        #mock chirpstack get_device() return value
        return_value = MagicMock()
        return_value.device = MagicMock()
        return_value.device.dev_eui = "9821230120031b00"
        return_value.device.name = "MFR Node"
        return_value.device.application_id = "ac81e18b-1925-47f9-839a-27d999a8af55"
        return_value.device.device_profile_id = "cf2aec2f-03e1-4a60-a32c-0faeef5730d8"
        return_value.created_at = MagicMock()
        return_value.created_at.seconds = 1695922619
        return_value.created_at.nanos = 943604000
        return_value.updated_at = MagicMock()
        return_value.updated_at.seconds = 1695923278
        return_value.updated_at.nanos = 943604000
        return_value.last_seen_at = MagicMock()
        return_value.last_seen_at.seconds = 1700675528
        return_value.last_seen_at.nanos = 993262000
        return_value.device_status = MagicMock()
        return_value.device_status.margin = 11
        return_value.device_status.external_power_source = True
        return_value.device_status.battery_level = -1

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_service_stub_instance.Get.return_value = return_value

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(mock_dev_eui)

        # Call the action in testing
        self.tracker.update_ld(mock_dev_eui, device_resp)

        #update data that should have been used
        data = {
            "name": replace_spaces(return_value.device.name),
            "battery_level": return_value.device_status.battery_level
        }

        # Assertions
        mock_django_patch.assert_called_once_with(f"{API_INTERFACE}/lorawandevices/{mock_dev_eui}/", headers=self.tracker.d_client.auth_header, json=data)