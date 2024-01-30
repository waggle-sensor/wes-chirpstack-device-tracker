import unittest
from pytest import mark
from unittest.mock import Mock, patch, MagicMock
from app.mqtt_client import *
import paho.mqtt.client as mqtt
from collections import namedtuple
from tools.chirpstack import MessageTemplate

MESSAGE = MessageTemplate().sample

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

class TestOnMessage(unittest.TestCase):

    def setUp(self):
        # Mock the MqttClient instance
        mock_args = Mock()
        self.mqtt_client = MqttClient(mock_args)
        #Mock the message
        self.Message = Mock()
        self.Message.payload = f'{MESSAGE}'.encode("utf-8")

    @patch('app.mqtt_client.logging')
    def test_on_message_happy_path(self, mock_logging):
        """
        Test on_message() happy path
        """
        expected_data = (
            "LORAWAN Message received by device Test device with deveui 0101010101010101:" + 
            self.Message.payload.decode("utf-8")
        )
        client = Mock()
        userdata = Mock()

        # Assert Logs
        with self.assertLogs(level='DEBUG') as log:
            # Call the on_message method
            self.mqtt_client.on_message(client, userdata, self.Message)
            self.assertEqual(len(log.output), 6)
            self.assertEqual(len(log.records), 6)
            self.assertIn(expected_data, log.output[0])
            self.assertIn("Signal Performance:", log.output[1])


class TestLogMessage(unittest.TestCase):

    def setUp(self):
        # Mock the MqttClient instance
        mock_args = Mock()
        self.mqtt_client = MqttClient(mock_args)
        #Mock the message
        self.Message = Mock()
        self.Message.payload = f'{MESSAGE}'.encode("utf-8")

    @patch('app.mqtt_client.logging')
    def test_log_message_happy_path(self, mock_logging):
        """
        Test log_message() happy path
        """
        expected_data = (
            "LORAWAN Message received by device Test device with deveui 0101010101010101:" + 
            self.Message.payload.decode("utf-8")
        )

        # Assert Logs
        with self.assertLogs(level='DEBUG') as log:
            # Call the log_message method
            self.mqtt_client.log_message(self.Message)
            self.assertEqual(len(log.output), 6)
            self.assertEqual(len(log.records), 6)
            self.assertIn(expected_data, log.output[0])
            self.assertIn("Signal Performance:", log.output[1])

    @patch('app.mqtt_client.MqttClient.parse_message')
    def test_log_message_Value_Error(self, mock_parse_message):
        """
        Test log_message() value error when parse_message returns less values to unpack
        """
        #Mock the return value for parse_message
        mock_parse_message.return_value = (None, {'deviceName': 'mock_device', 'devEui': 'mock_devEui'})

        # Assert Logs
        with self.assertLogs(level='ERROR') as log:
            # Call the log_message method
            with self.assertRaises(ValueError) as ve:
                self.mqtt_client.log_message(self.Message)
                self.assertEqual(len(log.output), 1)
                self.assertEqual(len(log.records), 1)
                self.assertIn(f"Message did not parse correctly, {ve}", log.output[0])


class TestParseMessage(unittest.TestCase):

    def setUp(self):
        # Mock the MqttClient instance
        mock_args = Mock()
        self.mqtt_client = MqttClient(mock_args)

    @patch('app.mqtt_client.parse_message_payload')
    def test_parse_message_returns_none(self, mock_parse_message_payload):
        """
        Test parse_message() returns none when parse_message_payload() returns an exception
        """
        # Mock the parse_message function Exception
        mock_parse_message_payload.side_effect = Exception("Mock decoding error")

        # Create a mock message object
        message = Mock()
        message.payload.decode.side_effect = Exception("Mock decoding error")

        # Call the parse_message function
        result = self.mqtt_client.parse_message(message)

        # Assert that the result is None
        self.assertIsNone(result)

class TestMqttClientRun(unittest.TestCase):

    @patch('app.mqtt_client.mqtt.Client')
    def test_run_happy_path(self, mock_mqtt_client):
        """
        Test the client's run() method's happy path
        """
        # Mock the connect method of the MQTT client
        mock_connect = mock_mqtt_client.return_value.connect
        mock_loop_forever = mock_mqtt_client.return_value.loop_forever

        # Create a mock arguments object
        mock_args = Mock(mqtt_server_ip='mock_ip', mqtt_server_port=1883, mqtt_subscribe_topic='mock_topic', vsn='mock_vsn')
        # Create an instance of MqttClient with the mock arguments
        mqtt_client = MqttClient(mock_args)

        # Assert Logs
        with self.assertLogs(level='INFO') as log:
            # Call the run method
            mqtt_client.run()
            self.assertEqual(len(log.output), 2)
            self.assertEqual(len(log.records), 2)
            self.assertIn(f"connecting [{mock_args.mqtt_server_ip}:{mock_args.mqtt_server_port}]...", log.output[0])
            self.assertIn("waiting for callback...", log.output[1])

        # Assert that the connect method was called with the correct arguments
        mock_connect.assert_called_once_with(host='mock_ip', port=1883, bind_address='0.0.0.0')

        # Assert that the loop_forever method was called
        mock_loop_forever.assert_called_once()

class TestGetDevice(unittest.TestCase):

    def test_get_device_valid_input(self):
        """
        Test Get_device() happy path
        """
        # Mock the input message_dict
        message_dict = {'deviceInfo': {
            'deviceName': 'TestDevice', 
            'devEui': '0123456789ABCDEF', 
            'deviceProfileId': '14855bf7-d10d-4aee-b618-ebfcb64dc7ad'
            }}

        # Call the Get_device function
        result = Get_device(message_dict)

        # Assert that the result is as expected
        self.assertEqual(
            result, 
            {
                'deviceName': 'TestDevice', 
                'devEui': '0123456789ABCDEF',
                'deviceProfileId': '14855bf7-d10d-4aee-b618-ebfcb64dc7ad'
            }
        )

    def test_get_device_missing_device_info(self):
        """
        Test Get_device() when message does not have deviceInfo
        """
        # Mock the input message_dict with missing deviceInfo
        message_dict = {'test':{}}

        # Call the Get_device function and expect a ValueError
        with self.assertRaises(TypeError):
            Get_device(message_dict)

    def test_get_device_missing_device_info_values(self):
        """
        Test Get_device() when deviceInfo is missing required values
        """
        # Mock the input message_dict with deviceInfo, but missing required values
        message_dict = {'deviceInfo': {}}

        # Call the Get_device function and expect a ValueError
        with self.assertRaises(KeyError):
            Get_device(message_dict)

class TestGetSignalPerformanceValues(unittest.TestCase):
    def test_get_signal_performance_values_valid_input(self):
        """
        Test Get_Signal_Performance_values()'s happy path
        """
        # Mock the input message_dict with valid values
        message_dict = {
            'rxInfo': [{'gatewayId': 'mock_gateway', 'rssi': -50, 'snr': 10}],
            'txInfo': {'modulation': {'lora': {'spreadingFactor': 12}}}
        }

        # Call the Get_Signal_Performance_values function
        result = Get_Signal_Performance_values(message_dict)

        # Assert that the result is as expected
        expected_result = {
            'rxInfo': [{'gatewayId': 'mock_gateway', 'rssi': -50, 'snr': 10}],
            'spreadingFactor': 12
        }
        self.assertEqual(result, expected_result)

    def test_get_signal_performance_values_missing_rx_info(self):
        """
        Test Get_Signal_Performance_values() when rxInfo is missing
        """
        # Mock the input message_dict with missing rxInfo
        message_dict = {
            'txInfo': {'modulation': {'lora': {'spreadingFactor': 12}}},
            "rxInfo": [{
                    "missing": "value",
            }]
        }

        # Call the Get_Signal_Performance_values function and expect a ValueError
        with self.assertRaises(ValueError):
            Get_Signal_Performance_values(message_dict)

    def test_get_signal_performance_values_missing_spreading_factor(self):
        """
        Test Get_Signal_Performance_values() when spreadingFactor is missing
        """
        # Mock the input message_dict with missing spreadingFactor
        message_dict = {
            'rxInfo': [{'gatewayId': 'mock_gateway', 'rssi': -50, 'snr': 10}],
            'txInfo': {'missing': "value"}
        }

        # Call the Get_Signal_Performance_values function and expect a ValueError
        with self.assertRaises(ValueError):
            Get_Signal_Performance_values(message_dict)

if __name__ == "__main__":
    unittest.main()