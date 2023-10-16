import grpc
from chirpstack_api import api
import logging
import os
import paho.mqtt.client as mqtt
import time

#TODO: change this to use kubernetes secrets
EMAIL = 'admin'
PASSWORD = 'admin'

#Pagination
LIMIT = 100 #Max number of records to return in the result-set.
OFFSET = LIMIT #Offset in the result-set (setting offset=limit goes to the next set of records aka next page)

class ChirpstackClient:
    def __init__(self, server):
        self.server = server
        self.channel = grpc.insecure_channel(self.server)
        self.auth_token = self.login()

    #Login to the server to get jwt auth token
    def login(self):
        client = api.InternalServiceStub(self.channel)

        # Construct the Login request.
        req = api.LoginRequest()
        req.email = EMAIL
        req.password = PASSWORD

        # Send the Login request.
        resp = client.Login(req)

        return resp.jwt

    #create network api keys using jwt auth token
    def create_api_key(self, jwt):
        client = api.InternalServiceStub(self.channel)

        # Define the JWT key metadata.
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        # Construct the CreateApiKey request.
        api_key = api.ApiKey(
            name='device-tracker',
            is_admin=True
        )
        req = api.CreateApiKeyRequest(api_key=api_key)

        # Send the CreateApiKey request.
        resp = client.CreateApiKey(req, metadata=metadata)

        return resp.token

    #list all devices by inputting the response of self.list_all_apps()
    def list_all_devices(self,app_resp):
        client = api.DeviceServiceStub(self.channel)

        # Define the JWT key metadata.
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        devices = []
        for app in app_resp:
            # Construct request.
            req = api.ListDevicesRequest()
            req.limit = LIMIT
            req.offset = 0 #get first page
            req.application_id = app.id #Application ID (UUID) to filter devices on.
            #req.search = "" #If set, the given string will be used to search on name (optional).

            devices.extend(self.List_agg_pagination(client,req,metadata))

        return devices

    #list all apps by inputting the response of self.list_tenants()
    def list_all_apps(self,tenant_resp):
        client = api.ApplicationServiceStub(self.channel)

        # Define the JWT key metadata.
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        apps = []

        for tenant in tenant_resp:
            # Construct request
            req = api.ListApplicationsRequest()
            req.limit = LIMIT
            req.offset = 0 #get first page
            req.tenant_id = tenant.id #Tenant ID to list the applications for.
            #req.search = "" #If set, the given string will be used to search on name (optional).

            apps.extend(self.List_agg_pagination(client,req,metadata))

        return apps

    #List all tenants
    def list_tenants(self):
        client = api.TenantServiceStub(self.channel)

        # Define the JWT key metadata.
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        #Construct request
        req = api.ListTenantsRequest()
        req.limit = LIMIT
        req.offset = 0 #get first page
        #req.search = "" #If set, the given string will be used to search on name (optional).
        #req.user_id = "" #If set, filters the result set to the tenants of the user. Only global API keys are able to filter by this field.

        return self.List_agg_pagination(client,req,metadata)

    def get_device_profile(self,device_profile_id):
        client = api.DeviceProfileServiceStub(self.channel)

        # Define the JWT key metadata.
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        #Construct request
        req = api.GetDeviceProfileRequest()
        req.id = device_profile_id

        return client.Get(req, metadata=metadata)

    #this method aggregates all the result-sets in pagination from rpc List into one list
    @staticmethod
    def List_agg_pagination(client,req,metadata):
        records=[]
        while True:
            resp = client.List(req, metadata=metadata)
            records.extend(resp.result)

            req.offset += OFFSET

            if (len(records) == resp.total_count):
                break

        return records

class MqttClient:
    def __init__(self, args):
        self.args = args
        self.client = self.configure_client()

    def configure_client(self):
        client_id = self.generate_client_id()
        client = mqtt.Client(client_id)
        client.on_subscribe = self.on_subscribe
        client.on_connect = self.on_connect
        #reconnect_delay_set: 
        # delay is the number of seconds to wait between successive reconnect attempts(default=1).
        # delay_max is the maximum number of seconds to wait between reconnection attempts(default=1)
        client.reconnect_delay_set(min_delay=5, max_delay=60)
        client.on_message = lambda client, userdata, message: self.dry_message(client, userdata, message)
        client.on_log = self.on_log

        return client

    @staticmethod
    def generate_client_id():
        hostname = os.uname().nodename
        process_id = os.getpid()
        return f"{hostname}-{process_id}"

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            client.subscribe(self.args.mqtt_subscribe_topic)
        else:
            logging.error(f"Connection to MQTT broker failed with code {rc}") 
        return

    @staticmethod
    def on_subscribe(client, obj, mid, granted_qos):
        logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))
        return

    @staticmethod
    def on_log(client, obj, level, string):
        logging.debug(string) #prints if args.debug = true
        return

    def dry_message(self, client, userdata, message):

        self.log_message(message)

        self.log_measurements(message)

        return

    @staticmethod
    def log_message(message):
            
        data = (
            "LORAWAN Message received: " + message.payload.decode("utf-8") + " with topic " + str(message.topic)
        )
        logging.info(data) #log message received

        return

    def log_measurements(self,message):

        try: #get metadata and measurements received
            metadata = parse_message_payload(message.payload.decode("utf-8"))
            measurements = metadata["object"]["measurements"]
        except:
            logging.error("Message did not contain measurements.")
            return

        Performance_vals = Get_Signal_Performance_values(metadata)
        
        for measurement in measurements:

            if self.args.collect: #true if not empty
                if measurement["name"] in self.args.collect: #if not empty only log measurements in list
                    logging.info(str(measurement["name"]) + ": " + str(measurement["value"]))
            else: #else collect is empty so log all measurements
                    logging.info(str(measurement["name"]) + ": " + str(measurement["value"]))

        for val in Performance_vals['rxInfo']:
            logging.info("gatewayId: " + str(val["gatewayId"]))
            logging.info("  rssi: " + str(val["rssi"]))
            logging.info("  snr: " + str(val["snr"]))
        logging.info("spreading factor: " + str(Performance_vals["spreadingFactor"]))

        return

    def run(self):
        logging.info(f"connecting [{self.args.mqtt_server_ip}:{self.args.mqtt_server_port}]...")
        self.client.connect(host=self.args.mqtt_server_ip, port=self.args.mqtt_server_port, bind_address="0.0.0.0")
        logging.info("waiting for callback...")
        self.client.loop_forever()