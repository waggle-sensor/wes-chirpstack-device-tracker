import os
import argparse
import logging
from pathlib import Path
from tracker import Tracker
from scalene import scalene_profiler

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

    if args.debug:
        # Start profiling
        scalene_profiler.start(output_file="/tmp/")

    tracker = Tracker(args)
    tracker.run()

    if args.debug:
        # Stop profiling
        scalene_profiler.stop()

if __name__ == "__main__":
    main()