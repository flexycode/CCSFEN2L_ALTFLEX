"""
Unit Tests for Address Validation.

TEST-P1-003: Comprehensive test suite for Ethereum address validation.

Tests cover:
- Valid address format recognition
- Invalid address rejection (wrong length, non-hex, missing prefix)
- EIP-55 checksum validation
- Zero address detection
- Pydantic schema validation integration
"""

import pytest
from pydantic import ValidationError

# Import validation utilities
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.address_validator import (
    is_valid_eth_address_format,
    is_valid_checksum,
    validate_eth_address,
    normalize_address,
    is_zero_address,
    validate_address_field,
    ETH_ADDRESS_PATTERN,
    ZERO_ADDRESS,
)

from app.schemas import (
    TransactionAnalysisRequest,
    AddressAnalysisRequest,
)


# =============================================================================
# Test Data
# =============================================================================

# Valid addresses
VALID_ADDRESSES = [
    "0x1234567890abcdef1234567890abcdef12345678",  # Lowercase
    "0x1234567890ABCDEF1234567890ABCDEF12345678",  # Uppercase
    "0xb66cd966670d962C227B3EABA30a872DbFb995db",  # Mixed case (checksummed)
    "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",  # Aave lending pool
    "0x0000000000000000000000000000000000000000",  # Zero address
]

# Invalid addresses
INVALID_ADDRESSES = [
    "",                                              # Empty
    "0x",                                            # Too short
    "0x123",                                         # Too short
    "0x1234567890abcdef1234567890abcdef1234567",    # 41 chars (missing 1)
    "0x1234567890abcdef1234567890abcdef123456789",  # 43 chars (extra 1)
    "1234567890abcdef1234567890abcdef12345678",     # Missing 0x prefix
    "0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",  # Non-hex characters
    "0x1234567890abcdef1234567890abcdef1234567@",   # Special character
    None,                                            # None type
    12345,                                           # Integer type
    "0x 1234567890abcdef1234567890abcdef12345678",  # Space in address
]


# =============================================================================
# Format Validation Tests
# =============================================================================

class TestAddressFormatValidation:
    """Tests for is_valid_eth_address_format function."""
    
    @pytest.mark.parametrize("address", VALID_ADDRESSES)
    def test_valid_addresses_pass(self, address):
        """Valid Ethereum addresses should pass format validation."""
        assert is_valid_eth_address_format(address) is True
    
    @pytest.mark.parametrize("address", INVALID_ADDRESSES)
    def test_invalid_addresses_fail(self, address):
        """Invalid addresses should fail format validation."""
        assert is_valid_eth_address_format(address) is False
    
    def test_case_insensitivity(self):
        """Format validation should accept both upper and lowercase hex."""
        lower = "0xabcdef1234567890abcdef1234567890abcdef12"
        upper = "0xABCDEF1234567890ABCDEF1234567890ABCDEF12"
        mixed = "0xAbCdEf1234567890AbCdEf1234567890AbCdEf12"
        
        assert is_valid_eth_address_format(lower) is True
        assert is_valid_eth_address_format(upper) is True
        assert is_valid_eth_address_format(mixed) is True


# =============================================================================
# Comprehensive Validation Tests
# =============================================================================

class TestComprehensiveValidation:
    """Tests for validate_eth_address function."""
    
    def test_valid_address_returns_success(self):
        """Valid address should return (True, '')."""
        is_valid, error = validate_eth_address("0x1234567890abcdef1234567890abcdef12345678")
        assert is_valid is True
        assert error == ""
    
    def test_empty_address_returns_error(self):
        """Empty address should return appropriate error."""
        is_valid, error = validate_eth_address("")
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_missing_prefix_returns_error(self):
        """Address without 0x prefix should return error."""
        is_valid, error = validate_eth_address("1234567890abcdef1234567890abcdef12345678")
        assert is_valid is False
        assert "0x" in error
    
    def test_wrong_length_returns_error(self):
        """Address with wrong length should return error with length info."""
        is_valid, error = validate_eth_address("0x123")
        assert is_valid is False
        assert "42" in error or "length" in error.lower()
    
    def test_invalid_hex_returns_error(self):
        """Address with non-hex characters should return error."""
        is_valid, error = validate_eth_address("0xGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
        assert is_valid is False
        assert "hex" in error.lower() or "invalid" in error.lower()
    
    def test_non_string_returns_error(self):
        """Non-string input should return error."""
        is_valid, error = validate_eth_address(12345)
        assert is_valid is False
        assert "string" in error.lower()


# =============================================================================
# Normalization Tests
# =============================================================================

class TestAddressNormalization:
    """Tests for normalize_address function."""
    
    def test_uppercase_normalized_to_lowercase(self):
        """Uppercase addresses should be normalized to lowercase."""
        upper = "0xABCDEF1234567890ABCDEF1234567890ABCDEF12"
        result = normalize_address(upper)
        assert result == upper.lower()
    
    def test_mixed_case_normalized_to_lowercase(self):
        """Mixed case addresses should be normalized to lowercase."""
        mixed = "0xAbCdEf1234567890AbCdEf1234567890AbCdEf12"
        result = normalize_address(mixed)
        assert result == mixed.lower()
    
    def test_invalid_address_raises_error(self):
        """Invalid address should raise ValueError."""
        with pytest.raises(ValueError):
            normalize_address("invalid")


# =============================================================================
# Zero Address Tests
# =============================================================================

class TestZeroAddress:
    """Tests for is_zero_address function."""
    
    def test_zero_address_detected(self):
        """Zero address should be detected."""
        assert is_zero_address(ZERO_ADDRESS) is True
    
    def test_zero_address_case_insensitive(self):
        """Zero address detection should be case insensitive."""
        upper_zero = "0x0000000000000000000000000000000000000000"
        assert is_zero_address(upper_zero) is True
    
    def test_non_zero_address_not_detected(self):
        """Non-zero addresses should not be detected as zero."""
        assert is_zero_address("0x1234567890abcdef1234567890abcdef12345678") is False
    
    def test_invalid_address_returns_false(self):
        """Invalid addresses should return False, not raise error."""
        assert is_zero_address("invalid") is False


# =============================================================================
# Checksum Validation Tests
# =============================================================================

class TestChecksumValidation:
    """Tests for EIP-55 checksum validation."""
    
    def test_all_lowercase_is_valid(self):
        """All-lowercase addresses are valid (non-checksummed)."""
        lower = "0xabcdef1234567890abcdef1234567890abcdef12"
        assert is_valid_checksum(lower) is True
    
    def test_all_uppercase_is_valid(self):
        """All-uppercase addresses are valid (non-checksummed)."""
        upper = "0xABCDEF1234567890ABCDEF1234567890ABCDEF12"
        assert is_valid_checksum(upper) is True
    
    def test_invalid_format_returns_false(self):
        """Invalid format should return False for checksum check."""
        assert is_valid_checksum("invalid") is False
        assert is_valid_checksum("0x123") is False


# =============================================================================
# Pydantic Schema Integration Tests
# =============================================================================

class TestSchemaValidation:
    """Tests for Pydantic schema address validation."""
    
    def test_transaction_request_valid_addresses(self):
        """TransactionAnalysisRequest should accept valid addresses."""
        request = TransactionAnalysisRequest(
            from_address="0x1234567890abcdef1234567890abcdef12345678",
            to_address="0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
            value_eth=1.0
        )
        # Addresses should be normalized to lowercase
        assert request.from_address == "0x1234567890abcdef1234567890abcdef12345678"
        assert request.to_address == "0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9"
    
    def test_transaction_request_rejects_invalid_from_address(self):
        """TransactionAnalysisRequest should reject invalid from_address."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionAnalysisRequest(
                from_address="invalid",
                to_address="0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
                value_eth=1.0
            )
        assert "from_address" in str(exc_info.value)
    
    def test_transaction_request_rejects_invalid_to_address(self):
        """TransactionAnalysisRequest should reject invalid to_address."""
        with pytest.raises(ValidationError) as exc_info:
            TransactionAnalysisRequest(
                from_address="0x1234567890abcdef1234567890abcdef12345678",
                to_address="not-an-address",
                value_eth=1.0
            )
        assert "to_address" in str(exc_info.value)
    
    def test_address_analysis_request_valid(self):
        """AddressAnalysisRequest should accept valid addresses."""
        request = AddressAnalysisRequest(
            address="0xb66cd966670d962C227B3EABA30a872DbFb995db"
        )
        # Address should be normalized to lowercase
        assert request.address == "0xb66cd966670d962c227b3eaba30a872dbfb995db"
    
    def test_address_analysis_request_rejects_invalid(self):
        """AddressAnalysisRequest should reject invalid addresses."""
        with pytest.raises(ValidationError) as exc_info:
            AddressAnalysisRequest(address="0x123")
        assert "address" in str(exc_info.value).lower()
    
    def test_address_request_rejects_empty(self):
        """AddressAnalysisRequest should reject empty address."""
        with pytest.raises(ValidationError):
            AddressAnalysisRequest(address="")
    
    def test_address_request_rejects_missing_prefix(self):
        """AddressAnalysisRequest should reject address without 0x prefix."""
        with pytest.raises(ValidationError):
            AddressAnalysisRequest(
                address="1234567890abcdef1234567890abcdef12345678"
            )


# =============================================================================
# Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_address_with_spaces_rejected(self):
        """Addresses with spaces should be rejected."""
        assert is_valid_eth_address_format(" 0x1234567890abcdef1234567890abcdef12345678") is False
        assert is_valid_eth_address_format("0x1234567890abcdef1234567890abcdef12345678 ") is False
        assert is_valid_eth_address_format("0x 1234567890abcdef1234567890abcdef12345678") is False
    
    def test_address_exactly_42_chars(self):
        """Address must be exactly 42 characters."""
        # 42 chars (valid)
        valid = "0x1234567890abcdef1234567890abcdef12345678"
        assert len(valid) == 42
        assert is_valid_eth_address_format(valid) is True
        
        # 41 chars (invalid)
        too_short = "0x1234567890abcdef1234567890abcdef1234567"
        assert len(too_short) == 41
        assert is_valid_eth_address_format(too_short) is False
        
        # 43 chars (invalid)
        too_long = "0x1234567890abcdef1234567890abcdef123456789"
        assert len(too_long) == 43
        assert is_valid_eth_address_format(too_long) is False
    
    def test_validate_address_field_raises_on_invalid(self):
        """validate_address_field should raise ValueError on invalid input."""
        with pytest.raises(ValueError):
            validate_address_field("invalid")
    
    def test_validate_address_field_normalizes_valid(self):
        """validate_address_field should normalize valid addresses."""
        result = validate_address_field("0xABCDEF1234567890ABCDEF1234567890ABCDEF12")
        assert result == "0xabcdef1234567890abcdef1234567890abcdef12"


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
