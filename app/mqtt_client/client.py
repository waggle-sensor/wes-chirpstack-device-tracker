import logging
import os
import paho.mqtt.client as mqtt
import time

class MqttClient:
    def __init__(self, args):
        self.args = args
        self.client = self.configure_client()

    def configure_client(self):
        client_id = self.generate_client_id()
        client = mqtt.Client(client_id)
        client.on_subscribe = self.on_subscribe
        client.on_connect = self.on_connect
        #reconnect_delay_set: 
        # delay is the number of seconds to wait between successive reconnect attempts(default=1).
        # delay_max is the maximum number of seconds to wait between reconnection attempts(default=1)
        client.reconnect_delay_set(min_delay=5, max_delay=60)
        client.on_message = lambda client, userdata, message: self.dry_message(client, userdata, message)
        client.on_log = self.on_log

        return client

    @staticmethod
    def generate_client_id():
        hostname = os.uname().nodename
        process_id = os.getpid()
        return f"{hostname}-{process_id}"

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT broker")
            client.subscribe(self.args.mqtt_subscribe_topic)
        else:
            logging.error(f"Connection to MQTT broker failed with code {rc}") 
        return

    @staticmethod
    def on_subscribe(client, obj, mid, granted_qos):
        logging.info("Subscribed: " + str(mid) + " " + str(granted_qos))
        return

    @staticmethod
    def on_log(client, obj, level, string):
        logging.debug(string) #prints if args.debug = true
        return

    def dry_message(self, client, userdata, message):

        self.log_message(message)

        self.log_measurements(message)

        return

    @staticmethod
    def log_message(message):
            
        data = (
            "LORAWAN Message received: " + message.payload.decode("utf-8") + " with topic " + str(message.topic)
        )
        logging.info(data) #log message received

        return

    def log_measurements(self,message):

        try: #get metadata and measurements received
            metadata = parse_message_payload(message.payload.decode("utf-8"))
            measurements = metadata["object"]["measurements"]
        except:
            logging.error("Message did not contain measurements.")
            return

        Performance_vals = Get_Signal_Performance_values(metadata)
        
        for measurement in measurements:

            if self.args.collect: #true if not empty
                if measurement["name"] in self.args.collect: #if not empty only log measurements in list
                    logging.info(str(measurement["name"]) + ": " + str(measurement["value"]))
            else: #else collect is empty so log all measurements
                    logging.info(str(measurement["name"]) + ": " + str(measurement["value"]))

        for val in Performance_vals['rxInfo']:
            logging.info("gatewayId: " + str(val["gatewayId"]))
            logging.info("  rssi: " + str(val["rssi"]))
            logging.info("  snr: " + str(val["snr"]))
        logging.info("spreading factor: " + str(Performance_vals["spreadingFactor"]))

        return

    def run(self):
        logging.info(f"connecting [{self.args.mqtt_server_ip}:{self.args.mqtt_server_port}]...")
        self.client.connect(host=self.args.mqtt_server_ip, port=self.args.mqtt_server_port, bind_address="0.0.0.0")
        logging.info("waiting for callback...")
        self.client.loop_forever()