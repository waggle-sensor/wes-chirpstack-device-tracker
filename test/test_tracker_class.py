import unittest
import requests
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

#TODO: add a test for Tracker.epoch_to_UTC()

def Mock_gd_ret_val():
    """
    Mock ChirpstackClient.get_device() return value
    """
    gd_ret_val = MagicMock()
    gd_ret_val.device = MagicMock()
    gd_ret_val.device.dev_eui = "9821230120031b00"
    gd_ret_val.device.name = "MFR Node"
    gd_ret_val.device.application_id = "ac81e18b-1925-47f9-839a-27d999a8af55"
    gd_ret_val.device.device_profile_id = "cf2aec2f-03e1-4a60-a32c-0faeef5730d8"
    gd_ret_val.created_at = MagicMock()
    gd_ret_val.created_at.seconds = 1695922619
    gd_ret_val.created_at.nanos = 943604000
    gd_ret_val.updated_at = MagicMock()
    gd_ret_val.updated_at.seconds = 1695923278
    gd_ret_val.updated_at.nanos = 943604000
    gd_ret_val.last_seen_at = MagicMock()
    gd_ret_val.last_seen_at.seconds = 1700675528
    gd_ret_val.last_seen_at.nanos = 993262000
    gd_ret_val.device_status = MagicMock()
    gd_ret_val.device_status.margin = 11
    gd_ret_val.device_status.external_power_source = True
    gd_ret_val.device_status.battery_level = -1

    return gd_ret_val

def Mock_gdp_ret_val():
    """
    Mock ChirpstackClient.get_device_profile() return value
    """
    gdp_ret_val = MagicMock()
    gdp_ret_val.device_profile = MagicMock()
    gdp_ret_val.device_profile.id = "cf2aec2f-03e1-4a60-a32c-0faeef5730d8"
    gdp_ret_val.device_profile.tenant_id = "52f14cd4-c6f1-4fbd-8f87-4025e1d49242"
    gdp_ret_val.device_profile.name = "MFR Node Profile"
    gdp_ret_val.device_profile.region = 2 #2 = US915
    gdp_ret_val.device_profile.mac_version = 2 #2 = LORAWAN_1_0_2
    gdp_ret_val.device_profile.reg_params_revision = 1 #1 = B
    gdp_ret_val.device_profile.adr_algorithm_id = "default"
    gdp_ret_val.device_profile.payload_codec_runtime = 1 #1 = JS
    gdp_ret_val.device_profile.payload_codec_script = "var=example\nreturn var;"
    gdp_ret_val.device_profile.flush_queue_on_activate = True
    gdp_ret_val.device_profile.uplink_interval = 1020
    gdp_ret_val.device_profile.device_status_req_interval = 10
    gdp_ret_val.device_profile.supports_otaa = True
    gdp_ret_val.device_profile.supports_otaa = True
    gdp_ret_val.device_profile.measurements = None
    gdp_ret_val.device_profile.auto_detect_measurements = True
    gdp_ret_val.created_at = MagicMock()
    gdp_ret_val.created_at.seconds = 1694716861
    gdp_ret_val.created_at.nanos = 633915000
    gdp_ret_val.updated_at = MagicMock()
    gdp_ret_val.updated_at.seconds = 1704991331
    gdp_ret_val.updated_at.nanos = 511071000

    return gdp_ret_val

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
        #mock ChirpstackClient.get_device() return value
        self.gd_ret_val = Mock_gd_ret_val()

    @patch("app.django_client.HttpMethod.PATCH")
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_update_ld_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_django_patch):
        """
        Successfully use chirpstack lorawan device data to call django's client update_ld()
        """
        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val

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
            "name": replace_spaces(self.gd_ret_val.device.name),
            "battery_level": self.gd_ret_val.device_status.battery_level
        }

        # Assertions
        mock_django_patch.assert_called_once_with(f"{API_INTERFACE}/lorawandevices/{mock_dev_eui}/", headers=self.tracker.d_client.auth_header, json=data)

class TestCreateLd(unittest.TestCase):

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
        #mock ChirpstackClient.get_device() return value
        self.gd_ret_val = Mock_gd_ret_val()

    @patch("app.django_client.HttpMethod.POST")
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_create_ld_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_django_post):
        """
        Successfully use chirpstack lorawan device data to call DjangoClient.create_ld()
        """
        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(mock_dev_eui)

        # Mock sensor hardware id in django
        mock_sh_id = "mock_sh_id"

        # Call the action in testing
        self.tracker.create_ld(mock_dev_eui, mock_sh_id, device_resp)

        #create data that should have been used
        data = {
            "name": replace_spaces(self.gd_ret_val.device.name),
            "battery_level": self.gd_ret_val.device_status.battery_level,
            "hardware": mock_sh_id,
            "deveui": mock_dev_eui
        }

        # Assertions
        mock_django_post.assert_called_once_with(f"{API_INTERFACE}/lorawandevices/", headers=self.tracker.d_client.auth_header, json=data)

class TestUpdateLc(unittest.TestCase):

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
        #mock ChirpstackClient.get_device() return value
        self.gd_ret_val = Mock_gd_ret_val() 
        #mock ChirpstackClient.get_device_profile() return value
        self.gdp_ret_val = Mock_gdp_ret_val()

    @patch("app.django_client.HttpMethod.PATCH")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_update_lc_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub, mock_django_patch):
        """
        Successfully use chirpstack lorawan device and device profile data 
        to call DjangoClient.update_lc()
        """
        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val

        # Mock the DeviceProfileServiceStub
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(mock_dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        # Call the action in testing
        self.tracker.update_lc(mock_dev_eui, device_resp, deviceprofile_resp)

        #update data that should have been used
        datetime_obj_utc = self.tracker.epoch_to_UTC(
            self.gd_ret_val.last_seen_at.seconds, 
            self.gd_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        con_type = "OTAA" if self.gdp_ret_val.device_profile.supports_otaa else "ABP"
        data = {
            "connection_name": replace_spaces(self.gd_ret_val.device.name),
            'last_seen_at': last_seen_at, 
            "margin": self.gd_ret_val.device_status.margin,
            "expected_uplink_interval_sec": self.gdp_ret_val.device_profile.uplink_interval,
            "connection_type": con_type
        }

        # Assertions
        mock_django_patch.assert_called_once_with(f"{API_INTERFACE}/lorawanconnections/{VSN}/{mock_dev_eui}/", headers=self.tracker.d_client.auth_header, json=data)

class TestCreateLc(unittest.TestCase):

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
        #mock ChirpstackClient.get_device() return value
        self.gd_ret_val = Mock_gd_ret_val() 
        #mock ChirpstackClient.get_device_profile() return value
        self.gdp_ret_val = Mock_gdp_ret_val()

    @patch("app.django_client.HttpMethod.POST")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_create_lc_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub, mock_django_post):
        """
        Successfully use chirpstack lorawan device and device profile data 
        to call DjangoClient.create_lc()
        """
        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val

        # Mock the DeviceProfileServiceStub
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(mock_dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        # Call the action in testing
        lc_uid = self.tracker.create_lc(mock_dev_eui, device_resp, deviceprofile_resp)

        #create data that should have been used
        datetime_obj_utc = self.tracker.epoch_to_UTC(
            self.gd_ret_val.last_seen_at.seconds, 
            self.gd_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        con_type = "OTAA" if self.gdp_ret_val.device_profile.supports_otaa else "ABP"
        data = {
            "node": VSN,
            "lorawan_device": mock_dev_eui,
            "connection_name": replace_spaces(self.gd_ret_val.device.name),
            'last_seen_at': last_seen_at, 
            "margin": self.gd_ret_val.device_status.margin,
            "expected_uplink_interval_sec": self.gdp_ret_val.device_profile.uplink_interval,
            "connection_type": con_type
        }

        # Assertions
        mock_django_post.assert_called_once_with(f"{API_INTERFACE}/lorawanconnections/", headers=self.tracker.d_client.auth_header, json=data)
        self.assertEqual(lc_uid, VSN + "-" + replace_spaces(device_resp.device.name) + "-" + mock_dev_eui)

    @patch("app.django_client.HttpMethod.POST")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_create_lc_no_response(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub, mock_django_post):
        """
        Test when DjangoClient.create_lc() returns no response
        """
        #Mock POST response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
        mock_django_post.return_value = mock_response

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock the DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val

        # Mock the DeviceProfileServiceStub
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(mock_dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        datetime_obj_utc = self.tracker.epoch_to_UTC(
            self.gd_ret_val.last_seen_at.seconds, 
            self.gd_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        con_type = "OTAA" if self.gdp_ret_val.device_profile.supports_otaa else "ABP"
        data = {
            "node": VSN,
            "lorawan_device": mock_dev_eui,
            "connection_name": replace_spaces(self.gd_ret_val.device.name),
            'last_seen_at': last_seen_at, 
            "margin": self.gd_ret_val.device_status.margin,
            "expected_uplink_interval_sec": self.gdp_ret_val.device_profile.uplink_interval,
            "connection_type": con_type
        }

        # Assertions
        with self.assertLogs(level='ERROR') as log:            
            # Call the method under test
            lc_uid = self.tracker.create_lc(mock_dev_eui, device_resp, deviceprofile_resp)

            # Assert
            self.assertEqual(len(log.output), 3)
            self.assertEqual(len(log.records), 3)
            self.assertIn("Tracker.create_lc(): d_client.create_lc() did not return a response", log.output[2])
            mock_django_post.assert_called_once_with(f"{API_INTERFACE}/lorawanconnections/", headers=self.tracker.d_client.auth_header, json=data)
            self.assertIsNone(lc_uid)