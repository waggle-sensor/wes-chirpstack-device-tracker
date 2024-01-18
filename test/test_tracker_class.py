import unittest
import requests
import copy
from unittest.mock import Mock, patch, MagicMock
from app.chirpstack_client import ChirpstackClient
from app.django_client import DjangoClient, HttpMethod
from app.tracker import Tracker
from app.tracker.parse import *
from app.tracker.convert_date import *
from app.manifest import Manifest
from tools.manifest import ManifestTemplate
from tools.chirpstack import MessageTemplate, Mock_ChirpstackClient_Methods

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
MANIFEST_FILEPATH = '/etc/waggle/node-manifest-v2.json'

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
        self.mock_chirp_methods = Mock_ChirpstackClient_Methods('mock_dev_eui')

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
        #mock return val
        mock_device_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(mock_dev_eui)

        #data that should have been used
        data = {
            "name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
            "battery_level": self.mock_chirp_methods.get_device_ret_val.device_status.battery_level
        }

        # Call the action in testing
        self.tracker.update_ld(mock_dev_eui, device_resp)

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
        self.mock_chirp_methods = Mock_ChirpstackClient_Methods('mock_dev_eui')

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

        # Mock DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        #mock return val
        mock_device_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(mock_dev_eui)

        # Mock sensor hardware id in django
        mock_sh_id = "mock_sh_id"

        #data that should have been used
        data = {
            "name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
            "battery_level": self.mock_chirp_methods.get_device_ret_val.device_status.battery_level,
            "hardware": mock_sh_id,
            "deveui": mock_dev_eui
        }

        # Call the action in testing
        self.tracker.create_ld(mock_dev_eui, mock_sh_id, device_resp)

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
        #mock ChirpstackClient method return values
        self.mock_chirp_methods = Mock_ChirpstackClient_Methods('mock_dev_eui')

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

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        #mock return vals
        mock_device_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

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
        datetime_obj_utc = epoch_to_UTC(
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.seconds, 
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        con_type = "OTAA" if self.mock_chirp_methods.get_device_profile_ret_val.device_profile.supports_otaa else "ABP"
        data = {
            "connection_name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
            'last_seen_at': last_seen_at, 
            "margin": self.mock_chirp_methods.get_device_ret_val.device_status.margin,
            "expected_uplink_interval_sec": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.uplink_interval,
            "connection_type": con_type
        }

        # Call the action in testing
        self.tracker.update_lc(mock_dev_eui, device_resp, deviceprofile_resp)

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
        #mock ChirpstackClient method return values
        self.mock_chirp_methods = Mock_ChirpstackClient_Methods('mock_dev_eui')

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

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        #mock return vals
        mock_device_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

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
        datetime_obj_utc = epoch_to_UTC(
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.seconds, 
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        con_type = "OTAA" if self.mock_chirp_methods.get_device_profile_ret_val.device_profile.supports_otaa else "ABP"
        data = {
            "node": VSN,
            "lorawan_device": mock_dev_eui,
            "connection_name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
            'last_seen_at': last_seen_at, 
            "margin": self.mock_chirp_methods.get_device_ret_val.device_status.margin,
            "expected_uplink_interval_sec": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.uplink_interval,
            "connection_type": con_type
        }

        # Call the action in testing
        lc_uid = self.tracker.create_lc(mock_dev_eui, device_resp, deviceprofile_resp)

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

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value
        
        #mock return vals
        mock_device_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

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
        datetime_obj_utc = epoch_to_UTC(
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.seconds, 
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        con_type = "OTAA" if self.mock_chirp_methods.get_device_profile_ret_val.device_profile.supports_otaa else "ABP"
        data = {
            "node": VSN,
            "lorawan_device": mock_dev_eui,
            "connection_name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
            'last_seen_at': last_seen_at, 
            "margin": self.mock_chirp_methods.get_device_ret_val.device_status.margin,
            "expected_uplink_interval_sec": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.uplink_interval,
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

class TestUpdateLk(unittest.TestCase):

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
        #mock ChirpstackClient method return values
        self.mock_chirp_methods = Mock_ChirpstackClient_Methods('mock_dev_eui')

    @patch("app.django_client.HttpMethod.PATCH")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_update_lk_otaa_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub, mock_django_patch):
        """
        Successfully use chirpstack lorawan device activation and device profile data 
        to call DjangoClient.update_lk() when the device is using OTAA
        """
        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.GetActivation.return_value = self.mock_chirp_methods.get_device_activation_ret_val
        mock_device_service_stub_instance.GetKeys.return_value = self.mock_chirp_methods.get_device_app_key_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get device activation
        act_resp = chirpstack_client.get_device_activation(mock_dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        lw_v = self.mock_chirp_methods.get_device_profile_ret_val.device_profile.mac_version
        key_resp = chirpstack_client.get_device_app_key(mock_dev_eui,lw_v)
        data = {
            "network_Key": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.nwk_s_enc_key, 
            "app_session_key": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.app_s_key,
            "dev_address": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.dev_addr,
            "app_key": key_resp
        }

        # Call the action in testing
        self.tracker.update_lk(mock_dev_eui, act_resp, deviceprofile_resp)

        # Assertions
        mock_django_patch.assert_called_once_with(f"{API_INTERFACE}/lorawankeys/{VSN}/{mock_dev_eui}/", headers=self.tracker.d_client.auth_header, json=data)

    @patch("app.django_client.HttpMethod.PATCH")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_update_lk_abp_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub, mock_django_patch):
        """
        Successfully use chirpstack lorawan device activation and device profile data 
        to call DjangoClient.update_lk() when the device is using ABP
        """
        #change to ABP
        self.mock_chirp_methods.get_device_profile_ret_val.device_profile.supports_otaa = False

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.GetActivation.return_value = self.mock_chirp_methods.get_device_activation_ret_val
        mock_device_service_stub_instance.GetKeys.return_value = self.mock_chirp_methods.get_device_app_key_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get device activation
        act_resp = chirpstack_client.get_device_activation(mock_dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        lw_v = self.mock_chirp_methods.get_device_profile_ret_val.device_profile.mac_version
        key_resp = chirpstack_client.get_device_app_key(mock_dev_eui,lw_v)
        data = {
            "network_Key": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.nwk_s_enc_key, 
            "app_session_key": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.app_s_key,
            "dev_address": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.dev_addr
        }

        # Call the action in testing
        self.tracker.update_lk(mock_dev_eui, act_resp, deviceprofile_resp)

        # Assertions
        mock_django_patch.assert_called_once_with(f"{API_INTERFACE}/lorawankeys/{VSN}/{mock_dev_eui}/", headers=self.tracker.d_client.auth_header, json=data)

class TestCreateLk(unittest.TestCase):

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
        #mock ChirpstackClient method return values
        self.mock_chirp_methods = Mock_ChirpstackClient_Methods('mock_dev_eui')

    @patch("app.django_client.HttpMethod.POST")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_create_lk_otaa_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub, mock_django_post):
        """
        Successfully use chirpstack lorawan device activation and device profile data 
        to call DjangoClient.create_lk() when the device is using OTAA
        """
        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.GetActivation.return_value = self.mock_chirp_methods.get_device_activation_ret_val
        mock_device_service_stub_instance.GetKeys.return_value = self.mock_chirp_methods.get_device_app_key_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get device activation
        act_resp = chirpstack_client.get_device_activation(mock_dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        mock_lc_str = "mock_lc_uid"
        lw_v = self.mock_chirp_methods.get_device_profile_ret_val.device_profile.mac_version
        key_resp = chirpstack_client.get_device_app_key(mock_dev_eui,lw_v)
        data = {
            "lorawan_connection": mock_lc_str,
            "network_Key": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.nwk_s_enc_key,  
            "app_session_key": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.app_s_key,
            "dev_address": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.dev_addr,
            "app_key": key_resp
        }

        # Call the action in testing
        self.tracker.create_lk(mock_dev_eui, mock_lc_str, act_resp, deviceprofile_resp)

        # Assertions
        mock_django_post.assert_called_once_with(f"{API_INTERFACE}/lorawankeys/", headers=self.tracker.d_client.auth_header, json=data)

    @patch("app.django_client.HttpMethod.POST")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_create_lk_abp_happy_path(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub, mock_django_post):
        """
        Successfully use chirpstack lorawan device activation and device profile data 
        to call DjangoClient.create_lk() when the device is using ABP
        """
        #change to ABP
        self.mock_chirp_methods.get_device_profile_ret_val.device_profile.supports_otaa = False

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.GetActivation.return_value = self.mock_chirp_methods.get_device_activation_ret_val
        mock_device_service_stub_instance.GetKeys.return_value = self.mock_chirp_methods.get_device_app_key_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get device activation
        act_resp = chirpstack_client.get_device_activation(mock_dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        mock_lc_str = "mock_lc_uid"
        lw_v = self.mock_chirp_methods.get_device_profile_ret_val.device_profile.mac_version
        key_resp = chirpstack_client.get_device_app_key(mock_dev_eui,lw_v)
        data = {
            "lorawan_connection": mock_lc_str,
            "network_Key": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.nwk_s_enc_key,  
            "app_session_key": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.app_s_key,
            "dev_address": self.mock_chirp_methods.get_device_activation_ret_val.device_activation.dev_addr
        }

        # Call the action in testing
        self.tracker.create_lk(mock_dev_eui, mock_lc_str, act_resp, deviceprofile_resp)

        # Assertions
        mock_django_post.assert_called_once_with(f"{API_INTERFACE}/lorawankeys/", headers=self.tracker.d_client.auth_header, json=data)

class TestCreateSh(unittest.TestCase):

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
        #mock ChirpstackClient method return values
        self.mock_chirp_methods = Mock_ChirpstackClient_Methods('mock_dev_eui')

    @patch("app.django_client.HttpMethod.POST")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_create_sh_happy_path(self, mock_insecure_channel, mock_device_profile_service_stub, mock_django_post):
        """
        Successfully use chirpstack lorawan device profile data 
        to call DjangoClient.create_sh()
        """
        #mock response of requests.post method
        headers = {
            'Content-Type': 'application/json', 
            'status-code': 201,
            'Custom-Header': 'Mocked-Value',
        }
        response_data = {
            "id": 1,
            "hardware": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.name,
            "hw_model": clean_hw_model(self.mock_chirp_methods.get_device_profile_ret_val.device_profile.name),
            "description": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.description,
            "capabilities": [35]
            }
        mock_response = Mock()
        mock_response.headers = headers
        mock_response.json.return_value = response_data
        mock_django_post.return_value = mock_response

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value
        # Mock return val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        data = {
            "hardware": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.name,
            "hw_model": clean_hw_model(self.mock_chirp_methods.get_device_profile_ret_val.device_profile.name),
            "description": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.description,
            "capabilities": [35]
        }

        # Call the action in testing
        sh_uid = self.tracker.create_sh(deviceprofile_resp)

        # Assertions
        mock_django_post.assert_called_once_with(f"{API_INTERFACE}/sensorhardwares/", headers=self.tracker.d_client.auth_header, json=data)
        self.assertEqual(sh_uid, response_data["id"])

    @patch("app.django_client.HttpMethod.POST")
    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_create_sh_no_response(self, mock_insecure_channel, mock_device_profile_service_stub, mock_django_post):
        """
        Test when DjangoClient.create_sh() returns an error
        """
        #mock response of requests.post method
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
        mock_django_post.return_value = mock_response

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value
        # Mock return val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        data = {
            "hardware": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.name,
            "hw_model": clean_hw_model(self.mock_chirp_methods.get_device_profile_ret_val.device_profile.name),
            "description": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.description,
            "capabilities": [35]
        }

        # Assertions
        with self.assertLogs(level='ERROR') as log:            
            # Call the action in testing
            sh_uid = self.tracker.create_sh(deviceprofile_resp)

            # Assert
            self.assertEqual(len(log.output), 3)
            self.assertEqual(len(log.records), 3)
            self.assertIn("Tracker.create_sh(): d_client.create_sh() did not return a response", log.output[2])
            mock_django_post.assert_called_once_with(f"{API_INTERFACE}/sensorhardwares/", headers=self.tracker.d_client.auth_header, json=data)
            self.assertIsNone(sh_uid)

class TestUpdateManifest(unittest.TestCase):

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
            chirpstack_account_password=CHIRPSTACK_ACT_PASSWORD,
            manifest=MANIFEST_FILEPATH
        )
        #set up manifest
        self.manifest = Manifest(self.args.manifest)
        self.manifest.dict = ManifestTemplate().sample
        #set up tracker
        self.tracker = Tracker(self.args)
        #mock ChirpstackClient method return values
        self.mock_chirp_methods = Mock_ChirpstackClient_Methods('mock_dev_eui')

    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_update_manifest_dev_exist(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub):
        """
        Successfully use chirpstack lorawan device and device profile data to
        to call Manifest.update_manifest() when device exists in the manifest
        """
        #change deveui to one existing in manifest sample
        self.mock_chirp_methods.edit_deveui("7d1f5420e81235c1")

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(self.mock_chirp_methods.get_device_ret_val.device.dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #updated lorawan entry should look like this
        con_type = "OTAA" if self.mock_chirp_methods.get_device_profile_ret_val.device_profile.supports_otaa else "ABP"
        datetime_obj_utc = epoch_to_UTC(
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.seconds, 
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        new_data = {
            "connection_name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
            "created_at": "2023-12-13T19:47:45.355000Z",
            "last_seen_at": last_seen_at,
            "margin": self.mock_chirp_methods.get_device_ret_val.device_status.margin, 
            "expected_uplink_interval_sec": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.uplink_interval,
            "connection_type": con_type,
            "lorawandevice": {
                "deveui": self.mock_chirp_methods.get_device_ret_val.device.dev_eui,
                "name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
                "battery_level": self.mock_chirp_methods.get_device_ret_val.device_status.battery_level,
                "hardware": {
                    "hardware": "Sap Flow Meter",
                    "hw_model": "SFM1x",
                    "hw_version": "",
                    "sw_version": "",
                    "manufacturer": "ICT International",
                    "datasheet": "https://ictinternational.com/manuals-and-brochures/sfm1x-sap-flow-meter/",
                    "capabilities": ["lorawan"],
                    "description": "# SFM1x Sap Flow Meter\r\n\r\nThe SFM1x Sap Flow Meter enables individual tree water use and health to be monitored in real time. This is because the SFM has integrated data transmission direct to cloud using IoT/LTE-M Cat-M1. The SFM1x Sap Flow Meter is a discrete standalone instrument based upon the Heat Ratio Method. This measurement principle has proven to be a robust and flexible technique to measure plant water use; being able to measure high, low, zero and reverse flows in a large range of plant anatomies & species from herbaceous to woody, and stem sizes > 10 mm in diameter. The theoretical basis and ratio metric design of the Heat Ratio Method makes possible the measurement of high, low, zero and reverse flows. The SFM1x Sap Flow Meter consists of two temperature sensing needles arranged equidistance above and below a central heater. These needles are inserted into the water conducting tissue of the plant by drilling 3 small parallel holes. Heat is then pulsed every 10 minutes into the water conducting tissue of the plant. The heat is used as a tracer to directly measure the velocity of water movement in the plant stem."
                },
            }
        }

        #call the action in testing
        self.tracker.update_manifest(self.mock_chirp_methods.get_device_ret_val.device.dev_eui, self.manifest, device_resp, deviceprofile_resp)

        #Assert if manifest dict was updated
        self.assertTrue(self.manifest.dict["lorawanconnections"][0] == new_data) #self.manifest.dict["lorawanconnections"][0] is 7d1f5420e81235c1 device

    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_update_manifest_dev_not_exist(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub):
        """
        Successfully use chirpstack lorawan device and device profile data to
        to call Manifest.update_manifest() when device DOES NOT exists in the manifest
        """
        #change deveui to non existing in manifest sample
        self.mock_chirp_methods.edit_deveui("12345678912345a3")

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.mock_chirp_methods.get_device_profile_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(self.mock_chirp_methods.get_device_ret_val.device.dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #new lorawan entry should look like this
        con_type = "OTAA" if self.mock_chirp_methods.get_device_profile_ret_val.device_profile.supports_otaa else "ABP"
        datetime_obj_utc = epoch_to_UTC(
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.seconds, 
            self.mock_chirp_methods.get_device_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        new_data = {
            "connection_name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
            "last_seen_at": last_seen_at,
            "margin": self.mock_chirp_methods.get_device_ret_val.device_status.margin, 
            "expected_uplink_interval_sec": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.uplink_interval,
            "connection_type": con_type,
            "lorawandevice": {
                "deveui": self.mock_chirp_methods.get_device_ret_val.device.dev_eui,
                "name": replace_spaces(self.mock_chirp_methods.get_device_ret_val.device.name),
                "battery_level": self.mock_chirp_methods.get_device_ret_val.device_status.battery_level,
                "hardware": {
                    "hardware": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.name,
                    "hw_model": clean_hw_model(self.mock_chirp_methods.get_device_profile_ret_val.device_profile.name),
                    "capabilities": ["lorawan"],
                    "description": self.mock_chirp_methods.get_device_profile_ret_val.device_profile.description
                },
            }
        }

        #call the action in testing
        self.tracker.update_manifest(self.mock_chirp_methods.get_device_ret_val.device.dev_eui, self.manifest, device_resp, deviceprofile_resp)

        #Assert if manifest dict was updated
        self.assertTrue(self.manifest.dict["lorawanconnections"][-1] == new_data)