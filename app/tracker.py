from argparse import Namespace
from chirpstack_client import ChirpstackClient
from django_client import DjangoClient
from mqtt_client import MqttClient

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