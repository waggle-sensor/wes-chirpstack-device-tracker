import os
import sys
import datetime
import grpc
from chirpstack_api import api
from chirpstack_client import ChirpstackClient
#from mqtt_client import MqttClient
import argparse
import logging
from pathlib import Path
from django_client import DjangoClient

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="enable debug logs")
    parser.add_argument(
        "--vsn",
        default=os.getenv("WAGGLE_NODE_VSN"),
        help="The Node's vsn.",
    )
    parser.add_argument(
        "--mqtt-server-ip",
        default=os.getenv("MQTT_SERVER_HOST"),
        help="MQTT server IP address",
    )
    parser.add_argument(
        "--mqtt-server-port",
        default=os.getenv("MQTT_SERVER_PORT"),
        help="MQTT server port",
        type=int,
    )
    parser.add_argument(
        "--mqtt-subscribe-topic",
        default=os.getenv("MQTT_SUBSCRIBE_TOPIC"),
        help="MQTT subscribe topic",
    )
    parser.add_argument(
        "--chirpstack-account-email",
        default=os.getenv("CHIRPSTACK_ACCOUNT_EMAIL"),
        help="The Chirpstack Account's email to use to access APIs",
    )
    parser.add_argument(
        "--chirpstack-account-password",
        default=os.getenv("CHIRPSTACK_ACCOUNT_PASSWORD"),
        help="The Chirpstack Account's password to use to access APIs",
    )
    parser.add_argument(
        "--chirpstack-api-interface",
        default=os.getenv("CHIRPSTACK_API_INTERFACE"),
        help="Chirpstack's server API interface. The port is usually 8080",
    )
    parser.add_argument(
        "--manifest",
        default=os.getenv("MANIFEST_FILE"),
        type=Path,
        help="path to node manifest file",
    )
    parser.add_argument(
        "--api-interface",
        default=os.getenv("API_INTERFACE"),
        help="API server interface.",
    )
    parser.add_argument(
        "--node-token",
        default=os.getenv("NODE_TOKEN"),
        help="The Node's token to access Django server API interface.",
    )
    parser.add_argument(
        "--lorawan-connection-router",
        default=os.getenv("LORAWANCONNECTION_ROUTER"),
        help="API server's Lorawan Connection Router.",
    )
    parser.add_argument(
        "--lorawan-key-router",
        default=os.getenv("LORAWANKEY_ROUTER"),
        help="API server's Lorawan Key Router.",
    )
    parser.add_argument(
        "--lorawan-device-router",
        default=os.getenv("LORAWANDEVICE_ROUTER"),
        help="API server's Lorawan Device Router.",
    )
    parser.add_argument(
        "--sensor-hardware-router",
        default=os.getenv("SENSORHARDWARE_ROUTER"),
        help="API server's Sensor Hardware Router.",
    )

    #get args
    args = parser.parse_args()

    #configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )

    #configure chirpstack client
    chirpstack_client = ChirpstackClient(args)

    test_eui = "2959df8baf3c667f"
    test_profile = "e7d0c6c3-0a68-4ae6-aa00-1e3c49918bce"
    mfr_eui = "98208e0000032a15"
    mfr_profile = "cf2aec2f-03e1-4a60-a32c-0faeef5730d8"

    device_resp = chirpstack_client.get_device(mfr_eui)
    deviceprofile_resp = chirpstack_client.get_device_profile(mfr_profile)
    act_resp = chirpstack_client.get_device_activation(mfr_eui)
    key_resp = chirpstack_client.get_device_app_key(mfr_eui,deviceprofile_resp.device_profile.mac_version)


    # print("device_resp:", device_resp)
    # print("\n")
    # print("\n")
    print("deviceprofile_resp:", deviceprofile_resp)
    print("\n")
    print("\n")
    # print("act_resp:", act_resp)
    # print("\n")
    # print("\n")
    # print("key_resp:", key_resp)
    print("\n")
    print("\n")
    print("lorawan_version:", deviceprofile_resp.device_profile.mac_version)

    # tenant_resp = chirpstack_client.list_tenants()

    # app_resp = chirpstack_client.list_all_apps(tenant_resp)

    # resp = chirpstack_client.list_all_devices(app_resp)

    # for device in resp:
    #     # Calculate the total seconds with nanoseconds
    #     total_seconds = device.last_seen_at.seconds + device.last_seen_at.nanos / 1e9
    #     # Convert seconds since epoch to a datetime object
    #     datetime_obj_utc = datetime.datetime.utcfromtimestamp(total_seconds)
    #     # Format the datetime object as a string
    #     formatted_date = datetime_obj_utc.strftime('%Y-%m-%d %H:%M:%S')

    #     print("Device ID:", device.dev_eui)
    #     print("Device Name:", device.name)
    #     print("Last seen at:", formatted_date) 
    #     print("Device App Keys:",chirpstack_client.get_device_app_key(device.dev_eui))
    #     print("Device Activation:",chirpstack_client.get_device_activation(device.dev_eui))
    #     print(device.device_status)
    #     print("\n")

    #     print(chirpstack_client.get_device_profile(device.device_profile_id))
        
    #TODO: uncomment once everything is ready to be ran in a pod and configure tracker
    # #configure mqtt client
    # mqtt_client = MqttClient(args)
    # mqtt_client.run()

if __name__ == "__main__":

    main()
