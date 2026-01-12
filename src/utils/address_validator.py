"""
Address Validation Utilities Module.

This module provides validation functions for Ethereum addresses,
including format validation and EIP-55 checksum verification.

Part of Phase 2 Security Enhancement (Sprint 1).
"""

import re
from typing import Tuple


# =============================================================================
# Constants
# =============================================================================

# Ethereum address regex pattern: 0x followed by exactly 40 hex characters
ETH_ADDRESS_PATTERN = re.compile(r'^0x[a-fA-F0-9]{40}$')

# Zero address (commonly used as burn address or null)
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


# =============================================================================
# Validation Functions
# =============================================================================

def is_valid_eth_address_format(address: str) -> bool:
    """
    Validate Ethereum address format using regex.
    
    Checks if the address:
    - Starts with '0x'
    - Contains exactly 40 hexadecimal characters after '0x'
    
    Args:
        address: The address string to validate
        
    Returns:
        True if format is valid, False otherwise
    """
    if not isinstance(address, str):
        return False
    return bool(ETH_ADDRESS_PATTERN.match(address))


def compute_checksum_address(address: str) -> str:
    """
    Compute the EIP-55 checksummed version of an Ethereum address.
    
    EIP-55 uses the hash of the lowercase address to determine
    which characters should be uppercase.
    
    Args:
        address: A valid Ethereum address (with or without checksum)
        
    Returns:
        The checksummed address string
        
    Raises:
        ValueError: If the address format is invalid
    """
    if not is_valid_eth_address_format(address):
        raise ValueError(f"Invalid Ethereum address format: {address}")
    
    # Remove 0x prefix and lowercase
    address_lower = address[2:].lower()
    
    # Compute keccak256 hash of the lowercase address
    try:
        from hashlib import sha3_256
        address_hash = sha3_256(address_lower.encode()).hexdigest()
    except ImportError:
        # Fallback: use pysha3 or pycryptodome if available
        try:
            import sha3
            address_hash = sha3.keccak_256(address_lower.encode()).hexdigest()
        except ImportError:
            try:
                from Crypto.Hash import keccak
                k = keccak.new(digest_bits=256)
                k.update(address_lower.encode())
                address_hash = k.hexdigest()
            except ImportError:
                # If no keccak available, skip checksum validation
                return "0x" + address_lower
    
    # Apply checksum: uppercase if corresponding hash nibble >= 8
    checksummed = ""
    for i, char in enumerate(address_lower):
        if char in '0123456789':
            checksummed += char
        elif int(address_hash[i], 16) >= 8:
            checksummed += char.upper()
        else:
            checksummed += char
    
    return "0x" + checksummed


def is_valid_checksum(address: str) -> bool:
    """
    Verify that an Ethereum address has a valid EIP-55 checksum.
    
    Note: All-lowercase and all-uppercase addresses are considered valid
    (they represent non-checksummed addresses).
    
    Args:
        address: The address string to validate
        
    Returns:
        True if checksum is valid or address is non-checksummed, False otherwise
    """
    if not is_valid_eth_address_format(address):
        return False
    
    # All lowercase or all uppercase (after 0x) are valid non-checksummed addresses
    address_body = address[2:]
    if address_body.islower() or address_body.isupper():
        return True
    
    # Mixed case: must match computed checksum
    try:
        return address == compute_checksum_address(address)
    except ValueError:
        return False


def validate_eth_address(address: str, require_checksum: bool = False) -> Tuple[bool, str]:
    """
    Comprehensive Ethereum address validation.
    
    Args:
        address: The address string to validate
        require_checksum: If True, require valid EIP-55 checksum
        
    Returns:
        Tuple of (is_valid, error_message)
        - If valid: (True, "")
        - If invalid: (False, "error description")
    """
    # Check type
    if not isinstance(address, str):
        return False, "Address must be a string"
    
    # Check empty
    if not address:
        return False, "Address cannot be empty"
    
    # Check 0x prefix
    if not address.startswith("0x"):
        return False, "Address must start with '0x'"
    
    # Check length (0x + 40 chars = 42)
    if len(address) != 42:
        return False, f"Address must be 42 characters, got {len(address)}"
    
    # Check hex format
    if not is_valid_eth_address_format(address):
        return False, "Address contains invalid characters (must be hexadecimal)"
    
    # Check checksum if required
    if require_checksum and not is_valid_checksum(address):
        return False, "Address has invalid EIP-55 checksum"
    
    return True, ""


def normalize_address(address: str) -> str:
    """
    Normalize an Ethereum address to lowercase with 0x prefix.
    
    Args:
        address: The address to normalize
        
    Returns:
        Normalized lowercase address
        
    Raises:
        ValueError: If address format is invalid
    """
    if not is_valid_eth_address_format(address):
        raise ValueError(f"Invalid Ethereum address format: {address}")
    return address.lower()


def is_zero_address(address: str) -> bool:
    """
    Check if an address is the zero/null address.
    
    Args:
        address: The address to check
        
    Returns:
        True if zero address, False otherwise
    """
    try:
        return normalize_address(address) == ZERO_ADDRESS
    except ValueError:
        return False


# =============================================================================
# Pydantic Validator (for use in schemas)
# =============================================================================

def validate_address_field(address: str) -> str:
    """
    Pydantic field validator for Ethereum addresses.
    
    Use this in Pydantic models with @field_validator decorator.
    
    Args:
        address: The address value to validate
        
    Returns:
        Normalized (lowercase) address
        
    Raises:
        ValueError: If validation fails
    """
    is_valid, error = validate_eth_address(address)
    if not is_valid:
        raise ValueError(error)
    return normalize_address(address)
