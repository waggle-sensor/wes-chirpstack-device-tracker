class MessageTemplate:
    def __init__(self):
        self.sample = """{
            "deduplicationId": "3ac7e3c4-4401-4b8d-9386-a5c902f9202d",
            "time": "2022-07-18T09:34:15.775023242+00:00",
            "payload": "",
            "deviceInfo": {
                "tenantId": "52f14cd4-c6f1-4fbd-8f87-4025e1d49242",
                "tenantName": "ChirpStack",
                "applicationId": "17c82e96-be03-4f38-aef3-f83d48582d97",
                "applicationName": "Test application",
                "deviceProfileId": "14855bf7-d10d-4aee-b618-ebfcb64dc7ad",
                "deviceProfileName": "Test device-profile",
                "deviceName": "Test device",
                "devEui": "0101010101010101",
                "tags": {
                    "key": "value"
                }
            },
            "devAddr": "00189440",
            "dr": 1,
            "fPort": 1,
            "data": "qg==",
            "rxInfo": [{
                "gatewayId": "0016c001f153a14c",
                "uplinkId": 4217106255,
                "rssi": -36,
                "snr": 10.5,
                "context": "E3OWOQ==",
                "metadata": {
                    "region_name": "eu868",
                    "region_common_name": "EU868"
                }
            }],
            "txInfo": {
                "frequency": 867100000,
                "modulation": {
                    "lora": {
                        "bandwidth": 125000,
                        "spreadingFactor": 11,
                        "codeRate": "CR_4_5"
                    }
                }
            }
        }"""