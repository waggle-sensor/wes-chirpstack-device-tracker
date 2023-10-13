import grpc
from chirpstack_api import api

#TODO: change this to use kubernetes secrets
EMAIL = 'admin'
PASSWORD = 'admin'

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

    #list devices in the app designated by app_id
    #TODO: list all devices by inputting an array of all app id(s)
    def list_devices(self,app_id):
        client = api.DeviceServiceStub(self.channel)

        # Define the JWT key metadata.
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        # Construct request.
        req = api.ListDevicesRequest()
        req.limit = 5 #Max number of devices to return in the result-set.
        #req.offset = 5 # Offset in the result-set (for pagination). Combination with limit only returns total_count
        #req.search = "MFR Node" #If set, the given string will be used to search on name (optional).
        req.application_id = app_id #Application ID (UUID) to filter devices on.

        resp = client.List(req, metadata=metadata)

        return resp