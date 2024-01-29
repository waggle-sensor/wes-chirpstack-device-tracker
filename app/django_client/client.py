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

    def __init__(self, args: Namespace):
        self.args = args
        self.server = self.args.api_interface
        self.vsn = self.args.vsn
        self.auth_token = self.args.node_token
        self.auth_header = {"Authorization": f"node_auth {self.auth_token}"}
        self.LC_ROUTER = self.args.lorawan_connection_router
        self.LK_ROUTER = self.args.lorawan_key_router
        self.LD_ROUTER = self.args.lorawan_device_router
        self.SH_ROUTER = self.args.sensor_hardware_router

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

    def update_lc(self, dev_eui: str, data: dict) -> dict:
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

    def ld_search(self, dev_eui: str) -> bool:
        """
        Search the db for a lorawan device return true if found
        """
        api_endpoint = f"{self.LD_ROUTER}{dev_eui}/"
        response = self.call_api(HttpMethod.GET, api_endpoint)

        if response:
            status_code = response['headers'].get('status-code')
            if status_code == 200:
                return True
            elif status_code == 404:
                return False
            else:
                logging.error(f"Unexpected status code in DjangoClient.ld_search() for {api_endpoint}: {status_code}")
                return False
        else:
            return False

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

    def sh_search(self, hw_model: str) -> bool:
        """
        Search the db for a sensor hardware return true if found
        """
        api_endpoint = f"{self.SH_ROUTER}{hw_model}/"
        response = self.call_api(HttpMethod.GET, api_endpoint)

        if response:
            status_code = response['headers'].get('status-code')
            if status_code == 200:
                return True
            elif status_code == 404:
                return False
            else:
                logging.error(f"Unexpected status code in DjangoClient.sh_search() for {api_endpoint}: {status_code}")
                return False
        else:
            return False

    def call_api(self, method: HttpMethod, endpoint: str, data: dict = None) -> dict:
        """
        Create request based on the method and call the api
        """
        api_url = urljoin(self.server, endpoint)
        try:
            if data is not None:
                response = method(api_url, headers=self.auth_header, json=data)
            else:
                response = method(api_url, headers=self.auth_header)
            response.raise_for_status() # Raise an exception for bad responses (4xx or 5xx)

            return {
                'headers': dict(response.headers),
                'json_body': response.json()
            }
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error occurred in DjangoClient.call_api() for {endpoint}: {e}")
            try:
                logging.error(f"    Details returned by server: {response.json()}")
            except requests.exceptions.JSONDecodeError as e:
                logging.error(f"requests.exceptions.JSONDecodeError: {e}")

            return None