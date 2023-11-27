import requests
import logging
import sys
import os
from urllib.parse import urljoin

class DjangoClient:
    """
    Django client to call Api(s)
    """
    def __init__(self, args):
        self.args = args
        self.server = self.args.django_api_interface
        self.vsn = self.args.vsn
        self.auth_token = self.args.node_token
        self.auth_header = {"Authorization": f"node_auth {self.auth_token}"}

    def get_lc(self, dev_eui):
        """
        Get LoRaWAN connection using dev EUI
        """
        api_endpoint = f"lorawanconnections/{self.vsn}/{dev_eui}/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.get(api_url, headers=self.auth_header)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        return response.json()

    def create_lc(self, data):
        """
        Create LoRaWAN connection
        """
        api_endpoint = "lorawanconnections/create/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.post(api_url, headers=self.auth_header, json=data)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        return response.json()

#    curl -X POST http://127.0.0.1:8000/lorawanconnections/create/ \
#     -H "Authorization: node_auth 8ce294ce5bf65c95f7e4c635605122ef5ae27826" \
#     -H "Content-Type: application/json" \
#     -d '{
#         "node": "W030",
#         "lorawan_device": "5556677",
#         "connection_name": "MyConnection",
#         "margin": 3.14,
#         "expected_uplink_interval_sec": 60,
#         "connection_type": "OTAA"
#     }'