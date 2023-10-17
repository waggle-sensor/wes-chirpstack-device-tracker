import logging
import os
import paho.mqtt.client as mqtt
import time

class MqttClient:
    def __init__(self, args):
        self.args = args
        self.client = self.configure_client()

    #configures the client
    def configure_client(self):
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

    #method that generate client name (a combination of vsn, container name, and process id)
    @staticmethod
    def generate_client_id():
        VSN = os.getenv("WAGGLE_NODE_VSN", "NONE")
        hostname = os.uname().nodename
        process_id = os.getpid()
        return f"{VSN}-{hostname}-{process_id}"

    #method to run when connecting to mqtt broker
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            client.subscribe(self.args.mqtt_subscribe_topic)
        else:
            logging.error(f"Connection to MQTT broker failed with code {rc}") 
        return

    #method to run when subcribing to mqtt broker
    @staticmethod
    def on_subscribe(client, obj, mid, granted_qos):
        logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))
        return

    #method to run on log of client
    @staticmethod
    def on_log(client, obj, level, string):
        logging.debug(string) #prints if args.debug = true
        return

    #method to run when message is received
    def on_message(self, client, userdata, message):

        #log message if debug flag was passed
        self.log_message(message) if args.debug else None

        #parse message for metadata and deviceInfo. 
        result = self.parse_message(message)
        if result is not None:
            metadata, deviceInfo = result
        else:
            return

        #TODO: now that you have the device info you can read the manifest
        # and check if the device exist in lorawandevices

        return

    #log message received from mqtt broker for debugging
    @staticmethod
    def log_message(message):

        #parse message for metadata and deviceInfo. 
        result = self.parse_message(message)
        if result is not None:
            metadata, deviceInfo = result
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

    #parse message for metadata and device info
    @staticmethod
    def parse_message(message):

        try: #get metadata and try to get device info
            metadata = parse_message_payload(message.payload.decode("utf-8"))
            temp = metadata["deviceInfo"]
        except:
            return None

        deviceInfo = Get_device(metadata)

        return (metadata, deviceInfo)

    #Connect to MQTT broker
    def run(self):
        logging.info(f"connecting [{self.args.mqtt_server_ip}:{self.args.mqtt_server_port}]...")
        self.client.connect(host=self.args.mqtt_server_ip, port=self.args.mqtt_server_port, bind_address="0.0.0.0")
        logging.info("waiting for callback...")
        self.client.loop_forever()