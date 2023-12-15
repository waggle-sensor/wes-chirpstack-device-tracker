import unittest
from unittest.mock import Mock, patch, MagicMock
from app.mqtt_client import MqttClient
import paho.mqtt.client as mqtt
from collections import namedtuple
from msg_sample import MESSAGE #TODO: use factories or add more sample data in txt/csv file
import json

class TestConfigureClient(unittest.TestCase):

    @patch('app.mqtt_client.mqtt.Client')
    def test_configure_client_happy_path(self, mock_mqtt_client):
        """
        Test configure_client() happy path
        """
        # Mock the arguments
        mock_args = Mock(vsn="mock_vsn")

        # Create a MqttClient instance
        mqtt_client = MqttClient(mock_args)

        # Assert the mqtt.Client is configured correctly
        mock_mqtt_client.return_value.reconnect_delay_set.assert_called_once_with(min_delay=5, max_delay=60)

        # Assert that the client attribute is set correctly
        self.assertEqual(mqtt_client.client, mock_mqtt_client.return_value)

class TestGenerateClientId(unittest.TestCase):

    def test_generate_client_id_happy_path(self):
        """
        Test generate_client_id() happy path
        """
        # Define a namedtuple for os.uname() return value
        UnameResult = namedtuple('UnameResult', ['nodename'])

        # Mock the return value for os.uname and os.getpid
        mock_uname = Mock(return_value=UnameResult(nodename='mock_nodename'))
        mock_getpid = Mock(return_value=12345)

        with unittest.mock.patch('app.mqtt_client.os.uname', mock_uname), \
             unittest.mock.patch('app.mqtt_client.os.getpid', mock_getpid):
            # Mock the arguments
            mock_args = Mock(vsn="mock_vsn")

            # Create a MqttClient instance
            mqtt_client = MqttClient(mock_args)

            # Call the method to test
            result = mqtt_client.generate_client_id()

            # Assert the generated client ID
            expected_client_id = 'mock_vsn-mock_nodename-12345'
            self.assertEqual(result, expected_client_id)

class TestOnConnect(unittest.TestCase):

    @patch('app.mqtt_client.logging')
    def test_on_connect_success(self, mock_logging):
        """
        Test on_connect() happy path
        """
        # Mock the arguments for on_connect
        client = Mock()
        userdata = Mock()
        flags = Mock()
        rc = 0

        # Mock the MqttClient instance
        mock_args = Mock(mqtt_subscribe_topic='mock_topic')
        mqtt_client = MqttClient(mock_args)

        # Assert Logs
        with self.assertLogs(level='INFO') as log:
            # Call the on_connect method
            mqtt_client.on_connect(client, userdata, flags, rc)
            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn("Connected to MQTT broker", log.output[0])

        # Assert that client.subscribe was called
        client.subscribe.assert_called_once_with('mock_topic')

    @patch('app.mqtt_client.logging')
    def test_on_connect_failure(self, mock_logging):
        """
        Test on_connect() connection failure
        """
        # Mock the arguments for on_connect
        client = Mock()
        userdata = Mock()
        flags = Mock()
        rc = 1 #simualte connection failure

        # Mock the MqttClient instance
        mock_args = Mock(mqtt_subscribe_topic='mock_topic')
        mqtt_client = MqttClient(mock_args)

        # Assert Logs
        with self.assertLogs(level='ERROR') as log:
            # Call the on_connect method
            mqtt_client.on_connect(client, userdata, flags, rc)
            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn(f"Connection to MQTT broker failed with code {rc}", log.output[0])

        # Assert that client.subscribe was not called
        client.subscribe.assert_not_called()

class TestOnSubscribe(unittest.TestCase):

    @patch('app.mqtt_client.logging')
    def test_on_subscribe_happy_path(self, mock_logging):
        """
        Test on_subscribe() happy path
        """
        # Mock the arguments for on_subscribe
        client = Mock()
        obj = Mock()
        mid = 123  # Mock message ID
        granted_qos = [1, 2, 0]  # Mock granted QoS levels

        # Mock the MqttClient instance
        mock_args = Mock()
        mqtt_client = MqttClient(mock_args)

        # Assert Logs
        with self.assertLogs(level='INFO') as log:
            # Call the on_subscribe method
            mqtt_client.on_subscribe(client, obj, mid, granted_qos)
            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn("Subscribed: 123 [1, 2, 0]", log.output[0])

class TestOnLog(unittest.TestCase):

    @patch('app.mqtt_client.logging')
    def test_on_log(self, mock_logging):
        """
        Test on_log() happy path
        """
        # Mock the arguments for on_subscribe
        client = Mock()
        obj = Mock()
        level = 20  # Mock log level (e.g., logging.DEBUG)
        string = "test"

        # Mock the MqttClient instance
        mock_args = Mock()
        mqtt_client = MqttClient(mock_args)

        # Assert Logs
        with self.assertLogs(level='DEBUG') as log:
            # Call the on_subscribe method
            mqtt_client.on_log(client, obj, level, string)
            self.assertEqual(len(log.output), 1)
            self.assertEqual(len(log.records), 1)
            self.assertIn("test", log.output[0])

#TODO: this function is still in progress
class TestOnMessage(unittest.TestCase):
    pass

class TestLogMessage(unittest.TestCase):

    @patch('app.mqtt_client.logging')
    def test_log_message_happy_path(self, mock_logging):
        """
        Test log_message() happy path
        """

        # Mock the MqttClient instance
        mock_args = Mock()
        mqtt_client = MqttClient(mock_args)

        #Mock the message
        class Message:
            def __init__(self, payload):
                self.payload = payload
        Msg = Message(f'{MESSAGE}'.encode("utf-8"))

        # Assert Logs
        with self.assertLogs(level='DEBUG') as log:
            # Call the log_message method
            mqtt_client.log_message(Msg)
            self.assertEqual(len(log.output), 6)
            self.assertEqual(len(log.records), 6)
            self.assertIn("Signal Performance:", log.output[1])

        # Assert that logging.debug was called with the expected data
        # expected_data = (
        #     "LORAWAN Message received by device mock_device with deveui mock_devEui:" + 
        #     message.payload.decode("utf-8")
        # )
        # mock_logging.debug.assert_any_call(expected_data)

        # Assert that logging.debug was called with Signal Performance information
        # mock_logging.debug.assert_any_call("Signal Performance:")
        # mock_logging.debug.assert_any_call("gatewayId: mock_gateway")
        # mock_logging.debug.assert_any_call("  rssi: -50")
        # mock_logging.debug.assert_any_call("  snr: 10")
        # mock_logging.debug.assert_any_call("spreading factor: 12")


if __name__ == '__main__':
    unittest.main()









if __name__ == "__main__":
    unittest.main()