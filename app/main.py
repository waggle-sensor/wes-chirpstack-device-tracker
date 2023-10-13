import os
import sys
import datetime
import pytz 
import grpc
from chirpstack_api import api



# Configuration.
server = "http://wes-chirpstack-server:8080"

# The DevEUI for which you want to enqueue the downlink.
#dev_eui = "0101010101010101"

# The API token (retrieved using the web-interface).
W030_api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6IjE0ZmQxYjU4LTU5MGItNDE2MS1iNjc2LTdlNzY3YTc1MGY0ZiIsInR5cCI6ImtleSJ9.Xhwz-tblD-zWXTzPnHIqutk7I5xazaddT2eGBzKALt4"
W039_api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6IjllZGVjNmY5LTIwYzAtNGMyYy04ZDdiLTBkOWExN2M2YTE5NiIsInR5cCI6ImtleSJ9.1F_mN6Q7rdJI2e_qeeUAaSychBVsoCE2uS51INfbktk"
api_token = W039_api_token

if __name__ == "__main__":
    # Connect without using TLS.
    channel = grpc.insecure_channel(server)

    # Device-queue API client.
    client = api.DeviceServiceStub(channel)

    # Define the API key meta-data.
    auth_token = [("authorization", "Bearer %s" % api_token)]

    # Construct request.
    req = api.ListDevicesRequest()
    req.limit = 5 #Max number of devices to return in the result-set.
    #req.offset = 5 # Offset in the result-set (for pagination). Combination with limit only returns total_count
    #req.search = "MFR Node" #If set, the given string will be used to search on name (optional).
    req.application_id = "ac81e18b-1925-47f9-839a-27d999a8af55" #Application ID (UUID) to filter devices on.
    #req.multicast_group_id = "" #Multicst-group ID (UUID) to filter devices on.
    #req.queue_item.confirmed = False
    #req.queue_item.data = bytes([0x01, 0x02, 0x03])
    #req.queue_item.dev_eui = dev_eui
    #req.queue_item.f_port = 10

    resp = client.List(req, metadata=auth_token)

    for device in resp.result:
        # Calculate the total seconds with nanoseconds
        total_seconds = device.last_seen_at.seconds + device.last_seen_at.nanos / 1e9
        # Convert seconds since epoch to a datetime object
        datetime_obj_utc = datetime.datetime.utcfromtimestamp(total_seconds)
        # Set the time zone to America/Chicago
        chicago_time_zone = pytz.timezone('America/Chicago')
        datetime_obj_chicago = datetime_obj_utc.replace(tzinfo=pytz.utc).astimezone(chicago_time_zone)
        # Format the datetime object as a string
        formatted_date = datetime_obj_chicago.strftime('%Y-%m-%d %H:%M:%S')

        print("Device ID:", device.dev_eui)
        print("Device Name:", device.name)
        print("Last seen at:", formatted_date) 
        print(device.device_status)
        print("\n")