import json
import logging

def parse_message_payload(payload_data):

    tmp_dict = json.loads(payload_data)

    return tmp_dict

def Get_device(message_dict):
    tmp_dict = {}

    #get values from nested dictionary
    deviceInfo_dict = message_dict.get('deviceInfo', None)
    try:
        tmp_dict['deviceName'] = deviceInfo_dict['deviceName']
        tmp_dict['devEui'] = deviceInfo_dict['devEui']
        tmp_dict['deviceProfileId'] = deviceInfo_dict['deviceProfileId']
    except TypeError as e:
        logging.error(f"Get_device(): {e}")
        raise TypeError(f"Get_device(): {e}")
    except KeyError as e:
        logging.error(f"Get_device(): {e}")
        raise KeyError(f"Get_device(): {e}")

    return tmp_dict

def Get_Signal_Performance_values(message_dict):
    tmp_dict = {}

    #Get Lorawan Performance values
    tmp_dict['rxInfo'] = []
    try:
        for val in message_dict['rxInfo']:
            temp = {"gatewayId":val['gatewayId'],"rssi":val['rssi'],"snr":val['snr']}
            tmp_dict['rxInfo'].append(temp)
    except:
        logging.error("rxInfo was not found")
        raise ValueError("rxInfo was not found")

    txInfo_dict = message_dict.get('txInfo', None)
    try:
        tmp_dict['spreadingFactor'] = txInfo_dict['modulation']["lora"]["spreadingFactor"]
    except:
        logging.error("spreadingFactor was not found")
        raise ValueError("spreadingFactor was not found")

    return tmp_dict