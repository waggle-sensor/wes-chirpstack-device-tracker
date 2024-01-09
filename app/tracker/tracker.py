from argparse import Namespace
from chirpstack_client import ChirpstackClient
from django_client import DjangoClient
from mqtt_client import MqttClient
from manifest import Manifest
from .parse import *

class Tracker(MqttClient):
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
                logging.error(f"Message did not parse correctly, {e}")
        else:
            return

        #TODO: now that you have the device info you can read the manifest
        # and check if the device exist in lorawandevices

        #load the node manifest
        manifest = Manifest(self.args.manifest)

        if manifest.lc_check():
            if manifest.ld_search(deviceInfo["devEui"]):
                #update lorawan connection and device in both db and manifest file

                #TODO: move a lot of this logic into their own methods

                #get device, device profile and more?
                device_resp = self.c_client.get_device(deviceInfo["devEui"])
                deviceprofile_resp = self.c_client.get_device_profile(deviceInfo["deviceProfileId"])
                
                #1) update ld
                battery_level = device_resp.device_status.battery_level
                name = replace_spaces(device_resp.device.name)
                ld_data = {
                    "device_name": name,
                    "battery_level": battery_level
                }
                self.d_client.update_ld(deviceInfo["devEui"], data)

                #2) update lc
                con_name = replace_spaces(device_resp.device.name)

                # Calculate the total seconds with nanoseconds #TODO: check if this converts the date correctly
                total_seconds = device_resp.last_seen_at.seconds + device_resp.last_seen_at.nanos / 1e9
                # Convert seconds since epoch to a datetime object
                datetime_obj_utc = datetime.datetime.utcfromtimestamp(total_seconds)
                
                last_seen_at = datetime_obj_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
                margin = device_resp.device_status.margin
                expected_upint = deviceprofile_resp.device_profile.uplink_interval
                con_type = "OTAA" if deviceprofile_resp.device_profile.supports_otaa else "ABP"
                lc_data = {
                    "connection_name": con_name,
                    'last_seen_at': last_seen_at, 
                    "margin": margin,
                    "expected_uplink_interval_sec": expected_upint,
                    "connection_type": con_type
                }
                self.d_client.update_lc(deviceInfo["devEui"], lc_data)

                #3) update lk
                #TODO: left off here on 01/09/2024 - Francisco Lozano

                
                #4) update manifest


                break
                return #<- remove, once done! 
            else:
                #try to retrieve device from db
                    #if not found create device in both db and manifest file
                    #else update device in both db and manifest file
                #create lorawan connection with device in both db and manifest file
                #create lorawan connection and device in both db and manifest file <-- make sure this is right
                #!!!! TODO: this is not right has to be outside the loop!
                return #<- remove, once done! 
        else:
            #try to retrieve device from db
                #if not found create device in db
                #else update device in db
            #create lorawan connection with device in both db and manifest file
            return #<- remove, once done! 


        return
    


    def update_lorawan_records(self):
        return

    def create_lorawan_records(self):
        return