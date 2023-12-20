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
        response.raise_for_status()  
        return response.json()

    def update_lc(self, dev_eui, data):
        """
        Update LoRaWAN connection
        """
        api_endpoint = f"lorawanconnections/update/{self.vsn}/{dev_eui}/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.patch(api_url, headers=self.auth_header, json=data)
        response.raise_for_status() 
        return response.json()

    def get_ld(self, dev_eui):
        """
        Get LoRaWAN device using dev EUI
        """
        api_endpoint = f"lorawandevices/{dev_eui}/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.get(api_url, headers=self.auth_header)
        response.raise_for_status()  
        return response.json()

    def create_ld(self, data):
        """
        Create LoRaWAN device
        """
        api_endpoint = "lorawandevices/create/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.post(api_url, headers=self.auth_header, json=data)
        response.raise_for_status()  
        return response.json()

    def update_ld(self, dev_eui, data):
        """
        Update LoRaWAN device
        """
        api_endpoint = f"lorawandevices/update/{dev_eui}/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.patch(api_url, headers=self.auth_header, json=data)
        response.raise_for_status()  
        return response.json()

    def get_lk(self, dev_eui):
        """
        Get LoRaWAN key using dev EUI
        """
        api_endpoint = f"lorawankeys/{self.vsn}/{dev_eui}/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.get(api_url, headers=self.auth_header)
        response.raise_for_status() 
        return response.json()

    def create_lk(self, data):
        """
        Create LoRaWAN key
        """
        api_endpoint = "lorawankeys/create/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.post(api_url, headers=self.auth_header, json=data)
        response.raise_for_status() 
        return response.json()

    def update_lk(self, dev_eui, data):
        """
        Update LoRaWAN key
        """
        api_endpoint = f"lorawankeys/update/{self.vsn}/{dev_eui}/"
        api_url = urljoin(self.server, api_endpoint)
        response = requests.patch(api_url, headers=self.auth_header, json=data)
        response.raise_for_status()  
        return response.json()