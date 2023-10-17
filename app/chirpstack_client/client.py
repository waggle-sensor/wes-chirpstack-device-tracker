import grpc
from chirpstack_api import api

#Pagination
LIMIT = 100 #Max number of records to return in the result-set.
OFFSET = LIMIT #Offset in the result-set (setting offset=limit goes to the next set of records aka next page)

class ChirpstackClient:
    def __init__(self, args, server):
        self.server = self.args.chirpstack_api_interface
        self.channel = grpc.insecure_channel(self.server)
        self.auth_token = self.login()
        self.email = self.args.chirpstack_account_email
        self.password = self.args.chirpstack_account_password

    #Login to the server to get jwt auth token
    def login(self):
        client = api.InternalServiceStub(self.channel)

        # Construct the Login request.
        req = api.LoginRequest()
        req.email = self.email
        req.password = self.password

        # Send the Login request.
        resp = client.Login(req)

        print(resp)

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