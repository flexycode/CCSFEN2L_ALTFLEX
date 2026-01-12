"""
Etherscan Collector Module.

This module handles fetching transaction histories and other blockchain data from Etherscan.
Extended in Sprint 2 to include on-chain address verification capabilities.
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class AddressVerificationResult:
    """Result of on-chain address verification."""
    address: str
    exists: bool
    is_contract: bool
    balance_wei: int
    balance_eth: float
    transaction_count: int
    first_tx_timestamp: Optional[int]
    first_tx_date: Optional[str]
    address_age_days: Optional[int]
    verification_timestamp: str
    error: Optional[str] = None


class EtherscanCollector:
    """
    Etherscan API collector for blockchain data and address verification.
    
    Provides methods for:
    - Fetching transaction history
    - Verifying address existence
    - Detecting contract vs EOA
    - Determining address age
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Etherscan collector.
        
        Args:
            api_key: Etherscan API key (defaults to ETHERSCAN_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ETHERSCAN_API_KEY', '')
        self.base_url = "https://api.etherscan.io/api"
    
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Etherscan API.
        
        Args:
            params: Query parameters for the API request
            
        Returns:
            JSON response from the API
            
        Raises:
            requests.RequestException: If the request fails
        """
        params['apikey'] = self.api_key
        response = requests.get(self.base_url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    # =========================================================================
    # Transaction Methods
    # =========================================================================
    
    def fetch_transactions(
        self, 
        address: str, 
        start_block: int = 0, 
        end_block: int = 99999999
    ) -> List[Dict[str, Any]]:
        """
        Fetch 'Normal' transactions by address.
        
        Args:
            address: Ethereum address to query
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            List of transaction dictionaries
        """
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'sort': 'asc',
        }
        try:
            data = self._make_request(params)
            if data.get('status') == '1':
                return data.get('result', [])
            else:
                print(f"Error fetching data: {data.get('message', 'Unknown error')}")
                return []
        except Exception as e:
            print(f"Exception occurred: {e}")
            return []
    
    # =========================================================================
    # Address Verification Methods (Sprint 2)
    # =========================================================================
    
    def get_balance(self, address: str) -> Tuple[int, Optional[str]]:
        """
        Get the ETH balance of an address.
        
        Args:
            address: Ethereum address to query
            
        Returns:
            Tuple of (balance_in_wei, error_message)
        """
        params = {
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
        }
        try:
            data = self._make_request(params)
            if data.get('status') == '1':
                return int(data.get('result', 0)), None
            else:
                return 0, data.get('message', 'Unknown error')
        except Exception as e:
            return 0, str(e)
    
    def get_transaction_count(self, address: str) -> Tuple[int, Optional[str]]:
        """
        Get the number of transactions for an address.
        
        Args:
            address: Ethereum address to query
            
        Returns:
            Tuple of (transaction_count, error_message)
        """
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': 1,  # We only need to check if any exist
            'sort': 'asc',
        }
        try:
            data = self._make_request(params)
            if data.get('status') == '1':
                # Get full count by fetching all
                full_params = params.copy()
                full_params['offset'] = 10000  # Max
                full_data = self._make_request(full_params)
                if full_data.get('status') == '1':
                    return len(full_data.get('result', [])), None
                return len(data.get('result', [])), None
            elif data.get('message') == 'No transactions found':
                return 0, None
            else:
                return 0, data.get('message', 'Unknown error')
        except Exception as e:
            return 0, str(e)
    
    def is_contract(self, address: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an address is a contract (has code) or an EOA.
        
        Uses the eth_getCode proxy endpoint.
        
        Args:
            address: Ethereum address to query
            
        Returns:
            Tuple of (is_contract, error_message)
        """
        params = {
            'module': 'proxy',
            'action': 'eth_getCode',
            'address': address,
            'tag': 'latest',
        }
        try:
            data = self._make_request(params)
            result = data.get('result', '0x')
            # Contract has code, EOA returns '0x' or '0x0'
            is_contract = result not in ('0x', '0x0', None, '')
            return is_contract, None
        except Exception as e:
            return False, str(e)
    
    def get_first_transaction(self, address: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Get the first transaction involving an address.
        
        Used to determine address age.
        
        Args:
            address: Ethereum address to query
            
        Returns:
            Tuple of (first_transaction, error_message)
        """
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'page': 1,
            'offset': 1,
            'sort': 'asc',
        }
        try:
            data = self._make_request(params)
            if data.get('status') == '1':
                results = data.get('result', [])
                if results:
                    return results[0], None
                return None, None
            elif data.get('message') == 'No transactions found':
                return None, None
            else:
                return None, data.get('message', 'Unknown error')
        except Exception as e:
            return None, str(e)
    
    def verify_address(self, address: str) -> AddressVerificationResult:
        """
        Perform comprehensive on-chain verification of an address.
        
        Checks:
        - Address existence (balance or transaction history)
        - Whether it's a contract or EOA
        - Address age (first transaction date)
        
        Args:
            address: Ethereum address to verify
            
        Returns:
            AddressVerificationResult with all verification data
        """
        errors = []
        
        # Get balance
        balance_wei, balance_error = self.get_balance(address)
        if balance_error:
            errors.append(f"Balance: {balance_error}")
        balance_eth = balance_wei / 1e18
        
        # Get transaction count
        tx_count, tx_error = self.get_transaction_count(address)
        if tx_error:
            errors.append(f"TxCount: {tx_error}")
        
        # Check if contract
        is_contract, contract_error = self.is_contract(address)
        if contract_error:
            errors.append(f"Contract: {contract_error}")
        
        # Get first transaction (address age)
        first_tx, first_tx_error = self.get_first_transaction(address)
        if first_tx_error:
            errors.append(f"FirstTx: {first_tx_error}")
        
        # Calculate address age
        first_tx_timestamp = None
        first_tx_date = None
        address_age_days = None
        
        if first_tx and 'timeStamp' in first_tx:
            first_tx_timestamp = int(first_tx['timeStamp'])
            first_tx_date = datetime.fromtimestamp(first_tx_timestamp).isoformat()
            age_seconds = datetime.now().timestamp() - first_tx_timestamp
            address_age_days = int(age_seconds / 86400)
        
        # Determine if address exists
        exists = balance_wei > 0 or tx_count > 0 or is_contract
        
        return AddressVerificationResult(
            address=address.lower(),
            exists=exists,
            is_contract=is_contract,
            balance_wei=balance_wei,
            balance_eth=balance_eth,
            transaction_count=tx_count,
            first_tx_timestamp=first_tx_timestamp,
            first_tx_date=first_tx_date,
            address_age_days=address_age_days,
            verification_timestamp=datetime.now().isoformat(),
            error="; ".join(errors) if errors else None
        )
    
    def address_exists(self, address: str) -> bool:
        """
        Quick check if an address exists on-chain.
        
        An address "exists" if it has:
        - Non-zero balance, OR
        - Any transaction history, OR
        - Contract code deployed
        
        Args:
            address: Ethereum address to check
            
        Returns:
            True if address exists on-chain
        """
        balance_wei, _ = self.get_balance(address)
        if balance_wei > 0:
            return True
        
        tx_count, _ = self.get_transaction_count(address)
        if tx_count > 0:
            return True
        
        is_contract, _ = self.is_contract(address)
        return is_contract


if __name__ == "__main__":
    # Example usage
    collector = EtherscanCollector()
    print("Etherscan Collector initialized.")
    
    # Test with a known address (Vitalik's address for example)
    test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    print(f"\nVerifying address: {test_address}")
    result = collector.verify_address(test_address)
    print(f"Exists: {result.exists}")
    print(f"Is Contract: {result.is_contract}")
    print(f"Balance: {result.balance_eth:.4f} ETH")
    print(f"Transaction Count: {result.transaction_count}")
    print(f"Address Age: {result.address_age_days} days")

