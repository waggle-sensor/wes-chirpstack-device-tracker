import os
import sys
import datetime
import pytz 
import grpc
from chirpstack_api import api
from client import ChirpstackClient

#TODO: uncomment the wes-chirpstack-sever when implemented in kubernetes cluster
#server = "http://wes-chirpstack-server:8080"
server = "localhost:8080"

if __name__ == "__main__":
    chirpstack_client = ChirpstackClient(server)

    tenant_resp = chirpstack_client.list_tenants()

    app_resp = chirpstack_client.list_all_apps(tenant_resp)

    resp = chirpstack_client.list_all_devices(app_resp)

    for device in resp:
        # Calculate the total seconds with nanoseconds
        total_seconds = device.last_seen_at.seconds + device.last_seen_at.nanos / 1e9
        # Convert seconds since epoch to a datetime object
        datetime_obj_utc = datetime.datetime.utcfromtimestamp(total_seconds)
        # Format the datetime object as a string
        formatted_date = datetime_obj_utc.strftime('%Y-%m-%d %H:%M:%S')

        print("Device ID:", device.dev_eui)
        print("Device Name:", device.name)
        print("Last seen at:", formatted_date) 
        print(device.device_status)
        print("\n")
