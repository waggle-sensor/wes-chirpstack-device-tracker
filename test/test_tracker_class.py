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

def Mock_gd_ret_val():
    """
    Mock ChirpstackClient.get_device() return value
    """
    val = MagicMock()
    val.device = MagicMock()
    val.device.dev_eui = "112123a120031b11"
    val.device.name = "mock device"
    val.device.application_id = "ac81e18b-1925-47f9-839a-27d999a8af11"
    val.device.device_profile_id = "cf2aec2f-03e1-4a60-a32c-0faeef5730c1"
    val.created_at = MagicMock()
    val.created_at.seconds = 1695922619
    val.created_at.nanos = 943604000
    val.updated_at = MagicMock()
    val.updated_at.seconds = 1695923278
    val.updated_at.nanos = 943604000
    val.last_seen_at = MagicMock()
    val.last_seen_at.seconds = 1700675528
    val.last_seen_at.nanos = 993262000
    val.device_status = MagicMock()
    val.device_status.margin = 11
    val.device_status.external_power_source = True
    val.device_status.battery_level = -1

    return val

def Mock_gdp_ret_val():
    """
    Mock ChirpstackClient.get_device_profile() return value
    """
    val = Mock()
    val.device_profile = Mock()
    val.device_profile.id = "cf2aec2f-03e1-4a60-a32c-0faeef5730d9"
    val.device_profile.tenant_id = "52f14cd4-c6f1-4fbd-8f87-4025e1d49241"
    val.device_profile.name = "Mock Profile"
    val.device_profile.description = "this is a mock profile"
    val.device_profile.region = 2 #2 = US915
    val.device_profile.mac_version = 2 #2 = LORAWAN_1_0_2
    val.device_profile.reg_params_revision = 1 #1 = B
    val.device_profile.adr_algorithm_id = "default"
    val.device_profile.payload_codec_runtime = 1 #1 = JS
    val.device_profile.payload_codec_script = "var=example\nreturn var;"
    val.device_profile.flush_queue_on_activate = True
    val.device_profile.uplink_interval = 1020
    val.device_profile.device_status_req_interval = 10
    val.device_profile.supports_otaa = True
    val.device_profile.measurements = None
    val.device_profile.auto_detect_measurements = True
    val.created_at = Mock()
    val.created_at.seconds = 1694716861
    val.created_at.nanos = 633915000
    val.updated_at = Mock()
    val.updated_at.seconds = 1704991331
    val.updated_at.nanos = 511071000

    return val

def Mock_gda_ret_val():
    """
    Mock ChirpstackClient.get_device_activation() return value
    """
    val = MagicMock()
    val.device_activation = MagicMock()
    val.device_activation.dev_eui = "112123a120031b11"
    val.device_activation.dev_addr = "00d65cd1"
    val.device_activation.app_s_key = "6e0f556d5975b872d744aee2c1239d5"
    val.device_activation.nwk_s_enc_key = "123456785975b872d744aee2a1239d12"
    val.device_activation.s_nwk_s_int_key = "1234567891023s89s53122s5678d9"
    val.device_activation.f_nwk_s_int_key = "23655489416521d5615a61651d652"
    val.device_activation.f_cnt_up = 200
    val.device_activation.n_f_cnt_down = 23
    val.device_activation.a_f_cnt_down = 10

    return val

def Mock_gdak_ret_val():
    """
    Mock ChirpstackClient.get_device_app_key() return value
    """
    val = MagicMock()
    val.device_keys = MagicMock()
    val.device_keys.dev_eui = "9821230120031b00"
    val.device_keys.nwk_key = "7e19d51b647b123dd123c484707aadc1"
    val.device_keys.app_key = "00000000000000000000000000000000"
    val.created_at = MagicMock()
    val.created_at.seconds = 1689015468
    val.created_at.nanos = 197740000
    val.updated_at = MagicMock()
    val.updated_at.seconds = 1700603333
    val.updated_at.nanos = 648973000

    return val

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
        #mock return val
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the dev_eui
        mock_dev_eui = "mock_dev_eui"

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(mock_dev_eui)

        #data that should have been used
        data = {
            "name": replace_spaces(self.gd_ret_val.device.name),
            "battery_level": self.gd_ret_val.device_status.battery_level
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

        # Mock DeviceServiceStub
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        #mock return val
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val

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
            "name": replace_spaces(self.gd_ret_val.device.name),
            "battery_level": self.gd_ret_val.device_status.battery_level,
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

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        #mock return vals
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val
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
        datetime_obj_utc = epoch_to_UTC(
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

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        #mock return vals
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val
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
        datetime_obj_utc = epoch_to_UTC(
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
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val
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
        datetime_obj_utc = epoch_to_UTC(
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
        self.gda_ret_val = Mock_gda_ret_val()
        self.gdp_ret_val = Mock_gdp_ret_val()
        self.gdak_ret_val = Mock_gdak_ret_val()

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
        mock_device_service_stub_instance.GetActivation.return_value = self.gda_ret_val
        mock_device_service_stub_instance.GetKeys.return_value = self.gdak_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

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
        lw_v = self.gdp_ret_val.device_profile.mac_version
        key_resp = chirpstack_client.get_device_app_key(mock_dev_eui,lw_v)
        data = {
            "network_Key": self.gda_ret_val.device_activation.nwk_s_enc_key, 
            "app_session_key": self.gda_ret_val.device_activation.app_s_key,
            "dev_address": self.gda_ret_val.device_activation.dev_addr,
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
        self.gdp_ret_val.device_profile.supports_otaa = False

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.GetActivation.return_value = self.gda_ret_val
        mock_device_service_stub_instance.GetKeys.return_value = self.gdak_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

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
        lw_v = self.gdp_ret_val.device_profile.mac_version
        key_resp = chirpstack_client.get_device_app_key(mock_dev_eui,lw_v)
        data = {
            "network_Key": self.gda_ret_val.device_activation.nwk_s_enc_key, 
            "app_session_key": self.gda_ret_val.device_activation.app_s_key,
            "dev_address": self.gda_ret_val.device_activation.dev_addr
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
        self.gda_ret_val = Mock_gda_ret_val()
        self.gdp_ret_val = Mock_gdp_ret_val()
        self.gdak_ret_val = Mock_gdak_ret_val()

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
        mock_device_service_stub_instance.GetActivation.return_value = self.gda_ret_val
        mock_device_service_stub_instance.GetKeys.return_value = self.gdak_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

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
        lw_v = self.gdp_ret_val.device_profile.mac_version
        key_resp = chirpstack_client.get_device_app_key(mock_dev_eui,lw_v)
        data = {
            "lorawan_connection": mock_lc_str,
            "network_Key": self.gda_ret_val.device_activation.nwk_s_enc_key,  
            "app_session_key": self.gda_ret_val.device_activation.app_s_key,
            "dev_address": self.gda_ret_val.device_activation.dev_addr,
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
        self.gdp_ret_val.device_profile.supports_otaa = False

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.GetActivation.return_value = self.gda_ret_val
        mock_device_service_stub_instance.GetKeys.return_value = self.gdak_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

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
        lw_v = self.gdp_ret_val.device_profile.mac_version
        key_resp = chirpstack_client.get_device_app_key(mock_dev_eui,lw_v)
        data = {
            "lorawan_connection": mock_lc_str,
            "network_Key": self.gda_ret_val.device_activation.nwk_s_enc_key,  
            "app_session_key": self.gda_ret_val.device_activation.app_s_key,
            "dev_address": self.gda_ret_val.device_activation.dev_addr
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
        self.gdp_ret_val = Mock_gdp_ret_val()

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
            "hardware": self.gdp_ret_val.device_profile.name,
            "hw_model": clean_hw_model(self.gdp_ret_val.device_profile.name),
            "description": self.gdp_ret_val.device_profile.description,
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
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        data = {
            "hardware": self.gdp_ret_val.device_profile.name,
            "hw_model": clean_hw_model(self.gdp_ret_val.device_profile.name),
            "description": self.gdp_ret_val.device_profile.description,
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
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #data that should have been used
        data = {
            "hardware": self.gdp_ret_val.device_profile.name,
            "hw_model": clean_hw_model(self.gdp_ret_val.device_profile.name),
            "description": self.gdp_ret_val.device_profile.description,
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
            chirpstack_account_password=CHIRPSTACK_ACT_PASSWORD
        )
        #set up manifest
        self.filepath = MANIFEST_FILEPATH
        self.manifest = Manifest(self.filepath)
        self.manifest.dict = ManifestTemplate().sample
        #set up tracker
        self.tracker = Tracker(self.args)
        #mock ChirpstackClient method return values
        self.gd_ret_val = Mock_gd_ret_val()
        self.gdp_ret_val = Mock_gdp_ret_val()

    @patch('app.chirpstack_client.api.DeviceProfileServiceStub')
    @patch('app.chirpstack_client.api.DeviceServiceStub')
    @patch('app.chirpstack_client.grpc.insecure_channel')
    def test_update_manifest_dev_exist(self, mock_insecure_channel, mock_device_service_stub, mock_device_profile_service_stub):
        """
        Successfully use chirpstack lorawan device and device profile data to
        to call Manifest.update_manifest() when device exists in the manifest
        """
        #change deveui to one existing in manifest sample
        self.gd_ret_val.device.dev_eui = "7d1f5420e81235c1"

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(self.gd_ret_val.device.dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #updated lorawan entry should look like this
        con_type = "OTAA" if self.gdp_ret_val.device_profile.supports_otaa else "ABP"
        datetime_obj_utc = epoch_to_UTC(
            self.gd_ret_val.last_seen_at.seconds, 
            self.gd_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        new_data = {
            "connection_name": replace_spaces(self.gd_ret_val.device.name),
            "created_at": "2023-12-13T19:47:45.355000Z",
            "last_seen_at": last_seen_at,
            "margin": self.gd_ret_val.device_status.margin, 
            "expected_uplink_interval_sec": self.gdp_ret_val.device_profile.uplink_interval,
            "connection_type": con_type,
            "lorawandevice": {
                "deveui": self.gd_ret_val.device.dev_eui,
                "name": replace_spaces(self.gd_ret_val.device.name),
                "battery_level": self.gd_ret_val.device_status.battery_level,
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
        self.tracker.update_manifest(self.gd_ret_val.device.dev_eui, self.manifest, device_resp, deviceprofile_resp)

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
        self.gd_ret_val.device.dev_eui = "12345678912345a3"

        # Mock the gRPC channel
        mock_channel = Mock()
        mock_insecure_channel.return_value = mock_channel

        # Mock stubs
        mock_device_service_stub_instance = mock_device_service_stub.return_value
        mock_device_profile_service_stub_instance = mock_device_profile_service_stub.return_value

        # Mock return values
        mock_device_service_stub_instance.Get.return_value = self.gd_ret_val
        mock_device_profile_service_stub_instance.Get.return_value = self.gdp_ret_val

        # Create a ChirpstackClient instance
        chirpstack_client = ChirpstackClient(self.args)

        # Call chirpstack_client get_device
        device_resp = chirpstack_client.get_device(self.gd_ret_val.device.dev_eui)

        # Mock the device profile ID
        mock_device_profile_id = "mock_device_profile_id"

        # Call get_device_profile
        deviceprofile_resp = chirpstack_client.get_device_profile(mock_device_profile_id)

        #new lorawan entry should look like this
        con_type = "OTAA" if self.gdp_ret_val.device_profile.supports_otaa else "ABP"
        datetime_obj_utc = epoch_to_UTC(
            self.gd_ret_val.last_seen_at.seconds, 
            self.gd_ret_val.last_seen_at.nanos
        )        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        new_data = {
            "connection_name": replace_spaces(self.gd_ret_val.device.name),
            "last_seen_at": last_seen_at,
            "margin": self.gd_ret_val.device_status.margin, 
            "expected_uplink_interval_sec": self.gdp_ret_val.device_profile.uplink_interval,
            "connection_type": con_type,
            "lorawandevice": {
                "deveui": self.gd_ret_val.device.dev_eui,
                "name": replace_spaces(self.gd_ret_val.device.name),
                "battery_level": self.gd_ret_val.device_status.battery_level,
                "hardware": {
                    "hardware": self.gdp_ret_val.device_profile.name,
                    "hw_model": clean_hw_model(self.gdp_ret_val.device_profile.name),
                    "capabilities": ["lorawan"],
                    "description": self.gdp_ret_val.device_profile.description
                },
            }
        }

        #call the action in testing
        self.tracker.update_manifest(self.gd_ret_val.device.dev_eui, self.manifest, device_resp, deviceprofile_resp)

        #Assert if manifest dict was updated
        self.assertTrue(self.manifest.dict["lorawanconnections"][-1] == new_data) 