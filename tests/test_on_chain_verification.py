"""
Unit Tests for On-Chain Address Verification.

Tests for Sprint 2: On-Chain Verification implementation.

Uses mocking to avoid hitting the real Etherscan API during tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from collectors.etherscan_collector import (
    EtherscanCollector,
    AddressVerificationResult,
)


# =============================================================================
# Test Data
# =============================================================================

VALID_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
CONTRACT_ADDRESS = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"  # Aave
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
EMPTY_ADDRESS = "0x1234567890abcdef1234567890abcdef12345678"

# Mock API responses
MOCK_BALANCE_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": "1000000000000000000"  # 1 ETH in wei
}

MOCK_EMPTY_BALANCE_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": "0"
}

MOCK_TX_LIST_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": [
        {
            "hash": "0xabc123",
            "from": "0xabc",
            "to": "0xdef",
            "value": "1000000000000000000",
            "timeStamp": "1609459200"  # Jan 1, 2021
        },
        {
            "hash": "0xdef456",
            "from": "0xdef",
            "to": "0xabc",
            "value": "500000000000000000",
            "timeStamp": "1609545600"
        }
    ]
}

MOCK_NO_TX_RESPONSE = {
    "status": "0",
    "message": "No transactions found",
    "result": []
}

MOCK_CONTRACT_CODE_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": "0x608060405234801561001057600080fd5b50"  # Contract bytecode
}

MOCK_EOA_CODE_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": "0x"  # No code = EOA
}


# =============================================================================
# EtherscanCollector Tests
# =============================================================================

class TestEtherscanCollector:
    """Tests for EtherscanCollector class."""
    
    @pytest.fixture
    def collector(self):
        """Create collector instance."""
        return EtherscanCollector(api_key="test_api_key")
    
    def test_initialization(self, collector):
        """Test collector initialization."""
        assert collector is not None
        assert collector.api_key == "test_api_key"
        assert collector.base_url == "https://api.etherscan.io/api"
    
    def test_initialization_from_env(self):
        """Test collector uses environment variable."""
        with patch.dict(os.environ, {"ETHERSCAN_API_KEY": "env_key"}):
            collector = EtherscanCollector()
            assert collector.api_key == "env_key"


class TestGetBalance:
    """Tests for get_balance method."""
    
    @pytest.fixture
    def collector(self):
        return EtherscanCollector(api_key="test_key")
    
    @patch('requests.get')
    def test_get_balance_success(self, mock_get, collector):
        """Test successful balance retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = MOCK_BALANCE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        balance, error = collector.get_balance(VALID_ADDRESS)
        
        assert balance == 1000000000000000000
        assert error is None
    
    @patch('requests.get')
    def test_get_balance_zero(self, mock_get, collector):
        """Test zero balance retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = MOCK_EMPTY_BALANCE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        balance, error = collector.get_balance(EMPTY_ADDRESS)
        
        assert balance == 0
        assert error is None
    
    @patch('requests.get')
    def test_get_balance_error(self, mock_get, collector):
        """Test balance retrieval with API error."""
        mock_get.side_effect = Exception("API Error")
        
        balance, error = collector.get_balance(VALID_ADDRESS)
        
        assert balance == 0
        assert error is not None
        assert "API Error" in error


class TestIsContract:
    """Tests for is_contract method."""
    
    @pytest.fixture
    def collector(self):
        return EtherscanCollector(api_key="test_key")
    
    @patch('requests.get')
    def test_is_contract_true(self, mock_get, collector):
        """Test contract detection."""
        mock_response = Mock()
        mock_response.json.return_value = MOCK_CONTRACT_CODE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        is_contract, error = collector.is_contract(CONTRACT_ADDRESS)
        
        assert is_contract is True
        assert error is None
    
    @patch('requests.get')
    def test_is_contract_false_eoa(self, mock_get, collector):
        """Test EOA detection (not a contract)."""
        mock_response = Mock()
        mock_response.json.return_value = MOCK_EOA_CODE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        is_contract, error = collector.is_contract(VALID_ADDRESS)
        
        assert is_contract is False
        assert error is None
    
    @patch('requests.get')
    def test_is_contract_error(self, mock_get, collector):
        """Test contract check with API error."""
        mock_get.side_effect = Exception("Network error")
        
        is_contract, error = collector.is_contract(VALID_ADDRESS)
        
        assert is_contract is False
        assert error is not None


class TestGetTransactionCount:
    """Tests for get_transaction_count method."""
    
    @pytest.fixture
    def collector(self):
        return EtherscanCollector(api_key="test_key")
    
    @patch('requests.get')
    def test_get_transaction_count_success(self, mock_get, collector):
        """Test successful transaction count retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = MOCK_TX_LIST_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        count, error = collector.get_transaction_count(VALID_ADDRESS)
        
        assert count >= 1
        assert error is None
    
    @patch('requests.get')
    def test_get_transaction_count_zero(self, mock_get, collector):
        """Test zero transaction count."""
        mock_response = Mock()
        mock_response.json.return_value = MOCK_NO_TX_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        count, error = collector.get_transaction_count(EMPTY_ADDRESS)
        
        assert count == 0
        assert error is None


class TestGetFirstTransaction:
    """Tests for get_first_transaction method."""
    
    @pytest.fixture
    def collector(self):
        return EtherscanCollector(api_key="test_key")
    
    @patch('requests.get')
    def test_get_first_transaction_success(self, mock_get, collector):
        """Test successful first transaction retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": [MOCK_TX_LIST_RESPONSE["result"][0]]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        first_tx, error = collector.get_first_transaction(VALID_ADDRESS)
        
        assert first_tx is not None
        assert "timeStamp" in first_tx
        assert error is None
    
    @patch('requests.get')
    def test_get_first_transaction_none(self, mock_get, collector):
        """Test no first transaction for new address."""
        mock_response = Mock()
        mock_response.json.return_value = MOCK_NO_TX_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        first_tx, error = collector.get_first_transaction(EMPTY_ADDRESS)
        
        assert first_tx is None
        assert error is None


class TestVerifyAddress:
    """Tests for verify_address comprehensive method."""
    
    @pytest.fixture
    def collector(self):
        return EtherscanCollector(api_key="test_key")
    
    @patch.object(EtherscanCollector, 'get_balance')
    @patch.object(EtherscanCollector, 'get_transaction_count')
    @patch.object(EtherscanCollector, 'is_contract')
    @patch.object(EtherscanCollector, 'get_first_transaction')
    def test_verify_address_existing_eoa(
        self, mock_first_tx, mock_contract, mock_tx_count, mock_balance, collector
    ):
        """Test verification of existing EOA."""
        mock_balance.return_value = (1000000000000000000, None)  # 1 ETH
        mock_tx_count.return_value = (50, None)
        mock_contract.return_value = (False, None)
        mock_first_tx.return_value = ({"timeStamp": "1609459200"}, None)
        
        result = collector.verify_address(VALID_ADDRESS)
        
        assert result.exists is True
        assert result.is_contract is False
        assert result.balance_eth == 1.0
        assert result.transaction_count == 50
        assert result.address_age_days is not None
        assert result.error is None
    
    @patch.object(EtherscanCollector, 'get_balance')
    @patch.object(EtherscanCollector, 'get_transaction_count')
    @patch.object(EtherscanCollector, 'is_contract')
    @patch.object(EtherscanCollector, 'get_first_transaction')
    def test_verify_address_contract(
        self, mock_first_tx, mock_contract, mock_tx_count, mock_balance, collector
    ):
        """Test verification of contract address."""
        mock_balance.return_value = (5000000000000000000, None)  # 5 ETH
        mock_tx_count.return_value = (1000, None)
        mock_contract.return_value = (True, None)
        mock_first_tx.return_value = ({"timeStamp": "1577836800"}, None)  # Jan 1, 2020
        
        result = collector.verify_address(CONTRACT_ADDRESS)
        
        assert result.exists is True
        assert result.is_contract is True
        assert result.balance_eth == 5.0
    
    @patch.object(EtherscanCollector, 'get_balance')
    @patch.object(EtherscanCollector, 'get_transaction_count')
    @patch.object(EtherscanCollector, 'is_contract')
    @patch.object(EtherscanCollector, 'get_first_transaction')
    def test_verify_address_nonexistent(
        self, mock_first_tx, mock_contract, mock_tx_count, mock_balance, collector
    ):
        """Test verification of non-existent address."""
        mock_balance.return_value = (0, None)
        mock_tx_count.return_value = (0, None)
        mock_contract.return_value = (False, None)
        mock_first_tx.return_value = (None, None)
        
        result = collector.verify_address(EMPTY_ADDRESS)
        
        assert result.exists is False
        assert result.is_contract is False
        assert result.balance_eth == 0.0
        assert result.transaction_count == 0
        assert result.address_age_days is None


class TestAddressExists:
    """Tests for address_exists quick check method."""
    
    @pytest.fixture
    def collector(self):
        return EtherscanCollector(api_key="test_key")
    
    @patch.object(EtherscanCollector, 'get_balance')
    @patch.object(EtherscanCollector, 'get_transaction_count')
    @patch.object(EtherscanCollector, 'is_contract')
    def test_address_exists_with_balance(
        self, mock_contract, mock_tx_count, mock_balance, collector
    ):
        """Test address exists due to balance."""
        mock_balance.return_value = (1000000000000000000, None)
        
        exists = collector.address_exists(VALID_ADDRESS)
        
        assert exists is True
        # Should return early, not call other methods
        mock_tx_count.assert_not_called()
        mock_contract.assert_not_called()
    
    @patch.object(EtherscanCollector, 'get_balance')
    @patch.object(EtherscanCollector, 'get_transaction_count')
    @patch.object(EtherscanCollector, 'is_contract')
    def test_address_exists_with_tx(
        self, mock_contract, mock_tx_count, mock_balance, collector
    ):
        """Test address exists due to transactions."""
        mock_balance.return_value = (0, None)
        mock_tx_count.return_value = (5, None)
        
        exists = collector.address_exists(VALID_ADDRESS)
        
        assert exists is True
        mock_contract.assert_not_called()
    
    @patch.object(EtherscanCollector, 'get_balance')
    @patch.object(EtherscanCollector, 'get_transaction_count')
    @patch.object(EtherscanCollector, 'is_contract')
    def test_address_exists_as_contract(
        self, mock_contract, mock_tx_count, mock_balance, collector
    ):
        """Test address exists as contract."""
        mock_balance.return_value = (0, None)
        mock_tx_count.return_value = (0, None)
        mock_contract.return_value = (True, None)
        
        exists = collector.address_exists(CONTRACT_ADDRESS)
        
        assert exists is True
    
    @patch.object(EtherscanCollector, 'get_balance')
    @patch.object(EtherscanCollector, 'get_transaction_count')
    @patch.object(EtherscanCollector, 'is_contract')
    def test_address_not_exists(
        self, mock_contract, mock_tx_count, mock_balance, collector
    ):
        """Test address does not exist."""
        mock_balance.return_value = (0, None)
        mock_tx_count.return_value = (0, None)
        mock_contract.return_value = (False, None)
        
        exists = collector.address_exists(EMPTY_ADDRESS)
        
        assert exists is False


# =============================================================================
# AddressVerificationResult Tests
# =============================================================================

class TestAddressVerificationResult:
    """Tests for AddressVerificationResult dataclass."""
    
    def test_create_result(self):
        """Test creating a verification result."""
        result = AddressVerificationResult(
            address="0xabc",
            exists=True,
            is_contract=False,
            balance_wei=1000000000000000000,
            balance_eth=1.0,
            transaction_count=10,
            first_tx_timestamp=1609459200,
            first_tx_date="2021-01-01T00:00:00",
            address_age_days=365,
            verification_timestamp="2022-01-01T00:00:00",
            error=None
        )
        
        assert result.address == "0xabc"
        assert result.exists is True
        assert result.balance_eth == 1.0
    
    def test_result_with_error(self):
        """Test result with error message."""
        result = AddressVerificationResult(
            address="0xabc",
            exists=False,
            is_contract=False,
            balance_wei=0,
            balance_eth=0.0,
            transaction_count=0,
            first_tx_timestamp=None,
            first_tx_date=None,
            address_age_days=None,
            verification_timestamp="2022-01-01T00:00:00",
            error="API rate limit exceeded"
        )
        
        assert result.error is not None
        assert "rate limit" in result.error


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
