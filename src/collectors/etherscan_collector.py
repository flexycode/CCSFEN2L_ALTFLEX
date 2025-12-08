"""
Etherscan Collector Module.

This module handles fetching transaction histories and other blockchain data from Etherscan.
"""

import requests
import json
import os

class EtherscanCollector:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ETHERSCAN_API_KEY')
        self.base_url = "https://api.etherscan.io/api"

    def fetch_transactions(self, address, start_block=0, end_block=99999999):
        """
        Fetches 'Normal' Transactions by Address
        """
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': 'asc',
            'apikey': self.api_key
        }
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            if data['status'] == '1':
                return data['result']
            else:
                print(f"Error fetching data: {data['message']}")
                return []
        except Exception as e:
            print(f"Exception occurred: {e}")
            return []

if __name__ == "__main__":
    # Example usage
    collector = EtherscanCollector()
    print("Etherscan Collector initialized.")
