import requests
import logging
import sys
import os
from urllib.parse import urljoin
from argparse import Namespace
from enum import Enum

class HttpMethod(Enum):
    GET = requests.get
    POST = requests.post
    PATCH = requests.patch

class DjangoClient:
    """
    Django client to call Api(s)
    """
    LC_ROUTER = "lorawanconnections/"
    LK_ROUTER = "lorawankeys/"
    LD_ROUTER = "lorawandevices/"
    SH_ROUTER = "sensorhardwares/"

    def __init__(self, args: Namespace):
        self.args = args
        self.server = self.args.django_api_interface
        self.vsn = self.args.vsn
        self.auth_token = self.args.node_token
        self.auth_header = {'Content-Type': 'application/json', "Authorization": f"node_auth {self.auth_token}"}

    def get_lc(self, dev_eui: str) -> dict:
        """
        Get LoRaWAN connection using dev EUI
        """
        api_endpoint = f"{self.LC_ROUTER}{self.vsn}/{dev_eui}/"
        return  self.call_api(HttpMethod.GET, api_endpoint)

    def create_lc(self, data: dict) -> dict:
        """
        Create LoRaWAN connection
        """
        api_endpoint = f"{self.LC_ROUTER}"
        return  self.call_api(HttpMethod.POST, api_endpoint, data)

    def update_lc(self, dev_eui: str, dat: dict) -> dict:
        """
        Update LoRaWAN connection
        """
        api_endpoint = f"{self.LC_ROUTER}{self.vsn}/{dev_eui}/"
        return  self.call_api(HttpMethod.PATCH, api_endpoint, data)

    def get_ld(self, dev_eui: str) -> dict:
        """
        Get LoRaWAN device using dev EUI
        """
        api_endpoint = f"{self.LD_ROUTER}{dev_eui}/"
        return  self.call_api(HttpMethod.GET, api_endpoint)

    def create_ld(self, data: dict) -> dict:
        """
        Create LoRaWAN device
        """
        api_endpoint = f"{self.LD_ROUTER}"
        return  self.call_api(HttpMethod.POST, api_endpoint, data)

    def update_ld(self, dev_eui: str, data: dict) -> dict:
        """
        Update LoRaWAN device
        """
        api_endpoint = f"{self.LD_ROUTER}{dev_eui}/"
        return  self.call_api(HttpMethod.PATCH, api_endpoint, data)

    def get_lk(self, dev_eui: str) -> dict:
        """
        Get LoRaWAN key using dev EUI
        """
        api_endpoint = f"{self.LK_ROUTER}{self.vsn}/{dev_eui}/"
        return  self.call_api(HttpMethod.GET, api_endpoint)

    def create_lk(self, data: dict) -> dict:
        """
        Create LoRaWAN key
        """
        api_endpoint = f"{self.LK_ROUTER}"
        return  self.call_api(HttpMethod.POST, api_endpoint, data)

    def update_lk(self, dev_eui: str, data: dict) -> dict:
        """
        Update LoRaWAN key
        """
        api_endpoint = f"{self.LK_ROUTER}{self.vsn}/{dev_eui}/"
        return  self.call_api(HttpMethod.PATCH, api_endpoint, data)

    def get_sh(self, hw_model: str) -> dict:
        """
        Get Sensor Hardware using hw_model
        """
        api_endpoint = f"{self.SH_ROUTER}{hw_model}/"
        return  self.call_api(HttpMethod.GET, api_endpoint)

    def create_sh(self, data: dict) -> dict:
        """
        Create Sensor Hardware
        """
        api_endpoint = f"{self.SH_ROUTER}"
        return self.call_api(HttpMethod.POST, api_endpoint, data)

    def update_sh(self, hw_model: str, data: dict) -> dict:
        """
        Update Sensor Hardware 
        """
        api_endpoint = f"{self.SH_ROUTER}{hw_model}/"
        return self.call_api(HttpMethod.PATCH, api_endpoint, data)

    def call_api(self, method: HttpMethod, endpoint: str, data: dict = None) -> dict:
        """
        Create request based on the method and call the api
        """
        api_url = urljoin(self.server, endpoint)

        try:
            response = method(api_url, headers=self.auth_header, json=data)
        except ValueError as e:
            logging.error(f"Unsupported method: {e}")
            raise ValueError(f"Unsupported method: {e}")
        except Exception as e:
            logging.error(f"Error occured: {e}")
            raise Exception(f"Error occured: {e}")
        response.raise_for_status() # Raise an exception for bad responses (4xx or 5xx)
        return response.json()