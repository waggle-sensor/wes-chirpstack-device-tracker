import os
import sys
import datetime
import grpc
from chirpstack_api import api
from chirpstack_client import ChirpstackClient
from mqtt_client import MqttClient
import argparse
import logging

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="enable debug logs")
    parser.add_argument(
        "--mqtt-server-ip",
        default=os.getenv("MQTT_SERVER_HOST", "wes-rabbitmq"),
        help="MQTT server IP address",
    )
    parser.add_argument(
        "--mqtt-server-port",
        default=os.getenv("MQTT_SERVER_PORT", "1883"),
        help="MQTT server port",
        type=int,
    )
    parser.add_argument(
        "--mqtt-subscribe-topic",
        default=os.getenv("MQTT_SUBSCRIBE_TOPIC", "application/#"),
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

    #get args
    args = parser.parse_args()

    #configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
    )

    #configure mqtt client
    mqtt_client = MqttClient(args)
    mqtt_client.run()

    chirpstack_client = ChirpstackClient(args)

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

        print(chirpstack_client.get_device_profile(device.device_profile_id))

if __name__ == "__main__":

    main()
