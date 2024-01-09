import logging
import os
import paho.mqtt.client as mqtt
import time
from .parse import *

class MqttClient:
    """
    Mqtt Client to subcribe to data streams
    """
    def __init__(self, args):
        self.args = args
        self.client = self.configure_client()

    def configure_client(self):
        """
        Configures the client
        """
        client_id = self.generate_client_id()
        client = mqtt.Client(client_id)
        client.on_subscribe = self.on_subscribe
        client.on_connect = self.on_connect
        #reconnect_delay_set: 
        # delay is the number of seconds to wait between successive reconnect attempts(default=1).
        # delay_max is the maximum number of seconds to wait between reconnection attempts(default=1)
        client.reconnect_delay_set(min_delay=5, max_delay=60)
        client.on_message = lambda client, userdata, message: self.on_message(client, userdata, message)
        client.on_log = self.on_log

        return client

    def generate_client_id(self):
        """
        Method that generates client name (a combination of vsn, container name, and process id)
        """
        hostname = os.uname().nodename
        process_id = os.getpid()
        return f"{self.args.vsn}-{hostname}-{process_id}"

    def on_connect(self, client, userdata, flags, rc):
        """
        Method to run when connecting to mqtt broker
        """
        if rc == 0:
            logging.info("Connected to MQTT broker")
            client.subscribe(self.args.mqtt_subscribe_topic)
        else:
            logging.error(f"Connection to MQTT broker failed with code {rc}") 
        return

    @staticmethod
    def on_subscribe(client, obj, mid, granted_qos):
        """
        Method to run when subcribing to mqtt broker
        """
        logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))
        return

    @staticmethod
    def on_log(client, obj, level, string):
        """
        Method to run on log of client
        """
        logging.debug(string) #prints if args.debug = true
        return

    def on_message(self, client, userdata, message):
        """
        Method to run when message is received
        """
        #log message if debug flag was passed
        self.log_message(message) if self.args.debug else None

        return

    def log_message(self, message):
        """
        Log message received from mqtt broker for debugging
        """
        #parse message for metadata and deviceInfo. 
        result = self.parse_message(message)
        if result is not None:
            try:
                metadata, deviceInfo = result
            except ValueError as e:
                logging.error(f"Message did not parse correctly, {e}")
                return
        else:
            return

        Performance_vals = Get_Signal_Performance_values(metadata)
            
        data = (
            "LORAWAN Message received by device " + deviceInfo['deviceName'] + 
            " with deveui " + deviceInfo['devEui']  + ":" + message.payload.decode("utf-8")
        )
        logging.debug(data)

        logging.debug("Signal Performance:")
        for val in Performance_vals['rxInfo']:
            logging.debug("gatewayId: " + str(val["gatewayId"]))
            logging.debug("  rssi: " + str(val["rssi"]))
            logging.debug("  snr: " + str(val["snr"]))
        logging.debug("spreading factor: " + str(Performance_vals["spreadingFactor"]))

        return

    @staticmethod
    def parse_message(message):
        """
        Parse message for metadata and device info
        """
        try: #get metadata and try to get device info
            metadata = parse_message_payload(message.payload.decode("utf-8"))
            deviceInfo = Get_device(metadata)
        except:
            return None

        return (metadata, deviceInfo)

    def run(self):
        """
        Connect to MQTT broker
        """
        logging.info(f"connecting [{self.args.mqtt_server_ip}:{self.args.mqtt_server_port}]...")
        self.client.connect(host=self.args.mqtt_server_ip, port=self.args.mqtt_server_port, bind_address="0.0.0.0")
        logging.info("waiting for callback...")
        self.client.loop_forever()