import grpc
from grpc import _channel as channel
from chirpstack_api import api
import logging
import sys

#Pagination
LIMIT = 100 #Max number of records to return in the result-set.
OFFSET = LIMIT #Offset in the result-set (setting offset=limit goes to the next set of records aka next page)

class ChirpstackClient:
    """
    Chirpstack client to call Api(s)
    """
    def __init__(self, args):
        self.args = args
        self.server = self.args.chirpstack_api_interface
        self.channel = grpc.insecure_channel(self.server)
        self.email = self.args.chirpstack_account_email
        self.password = self.args.chirpstack_account_password
        self.auth_token = self.login()

    def login(self):
        """
        Login to the server to get jwt auth token
        """
        client = api.InternalServiceStub(self.channel)

        # Construct the Login request.
        req = api.LoginRequest()
        req.email = self.email
        req.password = self.password

        # Send the Login request.
        logging.info(f"connecting {self.server}...")
        try:
            resp = client.Login(req)
        except grpc.RpcError as e:
            # Handle the exception here
            status_code = e.code()
            details = e.details()
            
            if status_code == grpc.StatusCode.UNAVAILABLE:
                logging.error("Service is unavailable. This might be a DNS resolution issue.")
                logging.error(f"Details: {details}")
            else:
                logging.error(f"An error occurred with status code {status_code}")
                logging.error(f"Details: {details}")

            # Exit with a non-zero status code to indicate failure
            sys.exit(1)
        except Exception as e:
            # Handle other exceptions if needed
            logging.error(f"An error occurred: {e}")

            # Exit with a non-zero status code to indicate failure
            sys.exit(1)
                
        logging.info("Connected to Chirpstack Server")

        return resp.jwt

    def list_all_devices(self,app_resp):
        """
        List all devices by inputting the response of self.list_all_apps()
        """
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

    def list_all_apps(self,tenant_resp):
        """
        List all apps by inputting the response of self.list_tenants()
        """
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

    def list_tenants(self):
        """
        List all tenants
        """
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
        """
        Get device profiles using profile id from self.list_all_devices() 
        """
        client = api.DeviceProfileServiceStub(self.channel)

        # Define the JWT key metadata.
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        #Construct request
        req = api.GetDeviceProfileRequest()
        req.id = device_profile_id

        return client.Get(req, metadata=metadata)
    
    def get_device_app_key(self,deveui):
        """
        Get device Application key using dev eui (Only OTAA)
        """
        client = api.DeviceServiceStub(self.channel)

        #define the JWT key metadata
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        #construct request
        req = api.GetDeviceKeysRequest()
        req.dev_eui = deveui

        try:
            resp = client.GetKeys(req, metadata=metadata)
        except grpc.RpcError as e:

            status_code = e.code()
            details = e.details()

            if status_code == grpc.StatusCode.NOT_FOUND:
                logging.error("The device key does not exist. It is possible that the device is using ABP which does not use an application key")
                logging.error(f"Details: {details}")
            else:
                logging.error(f"An error occurred with status code {status_code}")
                logging.error(f"Details: {details}")

            return
        except Exception as e:
            # Handle other exceptions
            logging.error(f"An error occurred: {e}")
            return
        
        return resp.device_keys.nwk_key

    def get_device_activation(self,deveui):
        """
        Get Activation returns the current activation details of the device (OTAA or ABP) using deveui
        """
        client = api.DeviceServiceStub(self.channel)

        #define the JWT key metadata
        metadata = [("authorization", "Bearer %s" % self.auth_token)]

        #construct request
        req = api.GetDeviceActivationRequest()
        req.dev_eui = deveui

        return client.GetActivation(req, metadata=metadata)

    @staticmethod
    def List_agg_pagination(client,req,metadata):
        """
        This method aggregates all the result-sets in pagination from rpc List into one list
        """
        records=[]
        while True:
            resp = client.List(req, metadata=metadata)
            records.extend(resp.result)

            req.offset += OFFSET

            if (len(records) == resp.total_count):
                break

        return records