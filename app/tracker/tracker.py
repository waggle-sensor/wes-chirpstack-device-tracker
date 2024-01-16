import datetime
import logging
from argparse import Namespace
from app.chirpstack_client import ChirpstackClient
from app.django_client import DjangoClient
from app.mqtt_client import MqttClient
from app.manifest import Manifest
from .parse import *

class Tracker(MqttClient):
    """
    A class that ties all clients together to track lorawan records
    """
    def __init__(self, args: Namespace):
        super().__init__(args)
        self.c_client = ChirpstackClient(args)
        self.d_client = DjangoClient(args)

    def on_message(self, client, userdata, message):
        """
        Method to run when Mqtt message is received
        """
        #log message if debug flag was passed
        self.log_message(message) if self.args.debug else None

        #parse message for metadata and deviceInfo. 
        result = self.parse_message(message)
        if result is not None:
            try:
                metadata, deviceInfo = result
            except ValueError as e:
                logging.error(f"Tracker.on_message(): Message did not parse correctly, {e}")
        else:
            return

        #load the node manifest
        manifest = Manifest(self.args.manifest)
        manifest_dev_exist = manifest.ld_search(deviceInfo["devEui"])

        #retrieve data from chirpstack
        device_resp = self.c_client.get_device(deviceInfo["devEui"])
        deviceprofile_resp = self.c_client.get_device_profile(deviceInfo["deviceProfileId"])
        act_resp = self.c_client.get_device_activation(deviceInfo["devEui"])

        # if lorawan device exist in manifest then...
        if manifest_dev_exist:
            #update lorawan device, connection, and key                
            self.update_ld(deviceInfo["devEui"], device_resp)
            self.update_lc(deviceInfo["devEui"], device_resp, deviceprofile_resp)
            self.update_lk(deviceInfo["devEui"], act_resp, deviceprofile_resp)

        #else lorawan device does not exist in manifest then...
        else:
            #if lorawan device exist in django then...
            if self.d_client.ld_search(deviceInfo["devEui"]): 
                # update lorawan device
                self.update_ld(deviceInfo["devEui"], device_resp)

            #else lorawan device does not exist in django then...
            else:
                #TODO: What is a better way to check if sensor hardware exists? 
                #   - whats a GUID for sensor hardwares that is shared throughout waggle that also does not change
                #   - hw_model will change since we will update it.
                #       - right now hw_model is filled as best as the tracker can
                #       - since we will change it, duplicates will be created
                hw_model = clean_hw_model(deviceprofile_resp.device_profile.name)
                # if sensor hardware exist in django then...
                if self.d_client.sh_search(hw_model):
                    # get sensor hardware from django
                    response = self.d_client.get_sh(hw_model)
                    sh_id = response['json_body'].get('id')
                #else sensor hardware does not exist in django then...
                else:
                    # create a new sensor hardware
                    sh_id = self.create_sh(deviceprofile_resp)
                
                # create a new lorawan device
                self.create_ld(deviceInfo["devEui"], sh_id, device_resp)
            
            #create a new lorawan connection and key
            lc_str = self.create_lc(deviceInfo["devEui"], device_resp, deviceprofile_resp)
            self.create_lk(deviceInfo["devEui"], lc_str, act_resp, deviceprofile_resp)

        #update manifest
        self.update_manifest(deviceInfo["devEui"], manifest_dev_exist, manifest, device_resp, deviceprofile_resp)
        return
    
    def update_ld(self, deveui: str, device_resp: dict):
        """
        Update lorawan device using mqtt message, chirpstack client, and django client
        device_resp: the output of chirpstack client's get_device
        """        
        battery_level = device_resp.device_status.battery_level
        dev_name = replace_spaces(device_resp.device.name)
        ld_data = {
            "name": dev_name,
            "battery_level": battery_level
        }
        self.d_client.update_ld(deveui, ld_data)

        return

    def create_ld(self, deveui: str, sh_id: int, device_resp: dict):
        """
        Create lorawan device using mqtt message, chirpstack client, and django client
        sh_id: sensor hardware record id in django
        device_resp: the output of chirpstack client's get_device
        """
        battery_level = device_resp.device_status.battery_level
        dev_name = replace_spaces(device_resp.device.name)
        ld_data = {
            "name": dev_name,
            "battery_level": battery_level,
            "hardware": sh_id,
            "deveui": deveui
        }
        self.d_client.create_ld(ld_data)

        return

    def update_lc(self, deveui: str, device_resp: dict, deviceprofile_resp: dict):
        """
        Update lorawan connection using mqtt message, chirpstack client, and django client
        device_resp: the output of chirpstack client's get_device()
        deviceprofile_resp: the output of chirpstack client's get_device_profile()
        """   
        dev_name = replace_spaces(device_resp.device.name)
        datetime_obj_utc = self.epoch_to_UTC(device_resp.last_seen_at.seconds, device_resp.last_seen_at.nanos)        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        margin = device_resp.device_status.margin
        expected_uplink = deviceprofile_resp.device_profile.uplink_interval
        con_type = "OTAA" if deviceprofile_resp.device_profile.supports_otaa else "ABP"
        lc_data = {
            "connection_name": dev_name,
            'last_seen_at': last_seen_at, 
            "margin": margin,
            "expected_uplink_interval_sec": expected_uplink,
            "connection_type": con_type
        }
        self.d_client.update_lc(deveui, lc_data)

        return

    def create_lc(self, deveui: str, device_resp: dict, deviceprofile_resp: dict) -> str:
        """
        Create a lorawan connection using mqtt message, chirpstack client, and django client
        device_resp: the output of chirpstack client's get_device()
        deviceprofile_resp: the output of chirpstack client's get_device_profile()
        """
        dev_name = replace_spaces(device_resp.device.name)
        datetime_obj_utc = self.epoch_to_UTC(device_resp.last_seen_at.seconds, device_resp.last_seen_at.nanos)        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        margin = device_resp.device_status.margin
        expected_uplink = deviceprofile_resp.device_profile.uplink_interval
        con_type = "OTAA" if deviceprofile_resp.device_profile.supports_otaa else "ABP"
        lc_data = {
            "node": self.args.vsn,
            "lorawan_device": deveui,
            "connection_name": dev_name,
            'last_seen_at': last_seen_at, 
            "margin": margin,
            "expected_uplink_interval_sec": expected_uplink,
            "connection_type": con_type
        }
        response = self.d_client.create_lc(lc_data)
        if response:
            lc_str = self.args.vsn + "-" + dev_name + "-" + deveui
            return lc_str
        else:
            logging.error("Tracker.create_lc(): d_client.create_lc() did not return a response")
            return None
        
    def update_lk(self, deveui: str, act_resp: dict, deviceprofile_resp: dict):
        """
        Update lorawan keys using mqtt message, chirpstack client, and django client
        act_resp: the output of chirpstack client's get_device_activation()
        deviceprofile_resp: the output of chirpstack client's get_device_profile()
        """
        con_type = "OTAA" if deviceprofile_resp.device_profile.supports_otaa else "ABP"
        nwk_key = act_resp.device_activation.nwk_s_enc_key
        app_s_key = act_resp.device_activation.app_s_key
        dev_adr = act_resp.device_activation.dev_addr
        lk_data = {
            "network_Key": nwk_key, 
            "app_session_key": app_s_key,
            "dev_address": dev_adr
        }
        if con_type == "OTAA":
            lw_v = deviceprofile_resp.device_profile.mac_version
            key_resp = self.c_client.get_device_app_key(deveui,lw_v)
            lk_data["app_key"] = key_resp
        self.d_client.update_lk(deveui, lk_data)

        return

    def create_lk(self, deveui: str, lc_str: str, act_resp: dict, deviceprofile_resp: dict):
        """
        Create lorawan keys using mqtt message, chirpstack client, and django client
        lc_str: the unique string of the lorawan connection. Used to reference the lorawan connection record
        act_resp: the output of chirpstack client's get_device_activation()
        deviceprofile_resp: the output of chirpstack client's get_device_profile()
        """
        con_type = "OTAA" if deviceprofile_resp.device_profile.supports_otaa else "ABP"
        nwk_key = act_resp.device_activation.nwk_s_enc_key
        app_s_key = act_resp.device_activation.app_s_key
        dev_adr = act_resp.device_activation.dev_addr
        lk_data = {
            "lorawan_connection": lc_str,
            "network_Key": nwk_key, 
            "app_session_key": app_s_key,
            "dev_address": dev_adr
        }
        if con_type == "OTAA":
            lw_v = deviceprofile_resp.device_profile.mac_version
            key_resp = self.c_client.get_device_app_key(deveui,lw_v)
            lk_data["app_key"] = key_resp
        self.d_client.update_lk(deveui, lk_data)

        return

    #TODO: consider using Tanuki to fill out fields like description, manufacturer, etc. in sensor hardware
    def create_sh(self, deviceprofile_resp: dict) -> int:
        """
        Create sensor hardware using django client. Returns the sensor hardware record id
        deviceprofile_resp: the output of chirpstack client's get_device_profile()
        """
        hardware = deviceprofile_resp.device_profile.name
        hw_model = clean_hw_model(deviceprofile_resp.device_profile.name)
        description = deviceprofile_resp.device_profile.description
        capabilities = [35] #lorawan = 35
        sh_data = {
            "hardware": hardware,
            "hw_model": hw_model,
            "description": description,
            "capabilities": capabilities
        }
        response = self.d_client.create_sh(sh_data)
        if response:
            return response.json.id
        else:
            logging.error("Tracker.create_sh(): d_client.create_sh() did not return a response")
            return None

    def update_manifest(self, deveui: str, dev_exist:bool, manifest: Manifest, device_resp: dict, deviceprofile_resp: dict):
        """
        Update manifest using mqtt message, chirpstack client, django client, and manifest
        dev_exist: boolean that tells if device exist in manifest
        manifest: Manifest object
        device_resp: the output of chirpstack client's get_device()
        deviceprofile_resp: the output of chirpstack client's get_device_profile()
        """
        datetime_obj_utc = self.epoch_to_UTC(device_resp.last_seen_at.seconds, device_resp.last_seen_at.nanos)        
        last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        margin = device_resp.device_status.margin
        expected_uplink = deviceprofile_resp.device_profile.uplink_interval
        con_type = "OTAA" if deviceprofile_resp.device_profile.supports_otaa else "ABP"
        battery_level = device_resp.device_status.battery_level
        dev_name = replace_spaces(device_resp.device.name)
        manifest_data = {
            "connection_name": dev_name,
            "last_seen_at": last_seen_at,
            "margin": margin,
            "expected_uplink_interval_sec": expected_uplink,
            "connection_type": con_type,
            "lorawandevice": {
                "deveui": deveui,
                "name": dev_name,
                "battery_level": battery_level,
            }
        }
        #include hardware in manifest_data when the device is not in manifest
        #TODO: consider using Tanuki to fill out fields like description, manufacturer, etc. in sensor hardware
        if not dev_exist:
            #Sensor hardware data is always coming from chirpstack client, so if django has updated
            #   sensor hardware data the manifest will not show it until update-stack.sh runs
            hardware = deviceprofile_resp.device_profile.name
            hw_model = clean_hw_model(deviceprofile_resp.device_profile.name)
            description = deviceprofile_resp.device_profile.description
            capabilities = ["lorawan"] 
            manifest_data["lorawandevice"]["hardware"] = {
                "hardware": hardware,
                "hw_model": hw_model,
                "description": description,
                "capabilities": capabilities
        }

        manifest.update_manifest(manifest_data)
        return

    @staticmethod
    def epoch_to_UTC(sec: int, nanos: int) -> datetime:
        """
        Convert seconds since epoch to a UTC datetime object
        """
        #TODO: check if this converts the date correctly
        total_seconds = sec + nanos / 1e9 # Calculate the total seconds with nanoseconds 
        datetime_obj_utc = datetime.datetime.utcfromtimestamp(total_seconds) # Convert seconds since epoch to a datetime object
        return datetime_obj_utc