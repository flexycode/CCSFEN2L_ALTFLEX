"""
Utils Package.

Utility modules for the AltFlex application.
"""

from .address_validator import (
    is_valid_eth_address_format,
    is_valid_checksum,
    validate_eth_address,
    normalize_address,
    compute_checksum_address,
    is_zero_address,
    validate_address_field,
)

# Note: address_verifier imports are conditional due to collector dependency
# Use: from utils.address_verifier import AddressVerifier, ComprehensiveAddressReport

__all__ = [
    # Address Validator (Sprint 1)
    "is_valid_eth_address_format",
    "is_valid_checksum",
    "validate_eth_address",
    "normalize_address",
    "compute_checksum_address",
    "is_zero_address",
    "validate_address_field",
]
