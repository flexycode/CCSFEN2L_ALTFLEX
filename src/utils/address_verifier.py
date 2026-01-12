"""
Address Verifier Utility Module.

High-level address verification utility that combines on-chain verification
with local validation for comprehensive address intelligence.

Part of Phase 2 Security Enhancement (Sprint 2).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Import collectors
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from collectors.etherscan_collector import EtherscanCollector, AddressVerificationResult
from utils.address_validator import (
    is_valid_eth_address_format,
    is_valid_checksum,
    validate_eth_address,
    normalize_address,
    is_zero_address,
)


@dataclass
class ComprehensiveAddressReport:
    """Complete address verification report combining local and on-chain checks."""
    
    # Address info
    address: str
    normalized_address: str
    
    # Local validation (Sprint 1)
    format_valid: bool
    checksum_valid: bool
    is_zero_address: bool
    
    # On-chain verification (Sprint 2)
    exists_on_chain: bool
    is_contract: bool
    balance_eth: float
    transaction_count: int
    address_age_days: Optional[int]
    first_activity_date: Optional[str]
    
    # Risk indicators
    is_new_address: bool  # Less than 30 days old
    is_dormant: bool  # No recent activity
    is_suspicious: bool  # Flagged for any reason
    
    # Metadata
    verification_timestamp: str
    errors: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class AddressVerifier:
    """
    High-level address verification utility.
    
    Combines:
    - Local format and checksum validation (Sprint 1)
    - On-chain verification via Etherscan (Sprint 2)
    - Risk assessment based on address characteristics
    """
    
    # Thresholds for risk assessment
    NEW_ADDRESS_THRESHOLD_DAYS = 30
    DORMANT_TX_THRESHOLD = 5
    
    def __init__(self, etherscan_api_key: Optional[str] = None):
        """
        Initialize the address verifier.
        
        Args:
            etherscan_api_key: Optional Etherscan API key
        """
        self.collector = EtherscanCollector(api_key=etherscan_api_key)
    
    def verify(self, address: str) -> ComprehensiveAddressReport:
        """
        Perform comprehensive address verification.
        
        Args:
            address: Ethereum address to verify
            
        Returns:
            ComprehensiveAddressReport with all verification results
        """
        errors = []
        
        # Local validation
        format_valid = is_valid_eth_address_format(address)
        checksum_valid = is_valid_checksum(address) if format_valid else False
        zero_address = is_zero_address(address) if format_valid else False
        
        # Normalize address
        try:
            normalized = normalize_address(address) if format_valid else address.lower()
        except ValueError:
            normalized = address.lower()
            errors.append("Could not normalize address")
        
        # On-chain verification (only if format is valid)
        if format_valid:
            on_chain_result = self.collector.verify_address(address)
            if on_chain_result.error:
                errors.append(on_chain_result.error)
        else:
            # Create empty result for invalid format
            on_chain_result = AddressVerificationResult(
                address=address.lower(),
                exists=False,
                is_contract=False,
                balance_wei=0,
                balance_eth=0.0,
                transaction_count=0,
                first_tx_timestamp=None,
                first_tx_date=None,
                address_age_days=None,
                verification_timestamp=datetime.now().isoformat(),
                error="Invalid address format - skipped on-chain verification"
            )
            errors.append("Invalid address format")
        
        # Risk assessment
        is_new = (
            on_chain_result.address_age_days is not None and 
            on_chain_result.address_age_days < self.NEW_ADDRESS_THRESHOLD_DAYS
        )
        is_dormant = on_chain_result.transaction_count < self.DORMANT_TX_THRESHOLD
        
        # Suspicious indicators
        suspicious_reasons = []
        if not format_valid:
            suspicious_reasons.append("Invalid format")
        if zero_address:
            suspicious_reasons.append("Zero address")
        if is_new and on_chain_result.transaction_count > 100:
            suspicious_reasons.append("New address with high tx count")
        
        is_suspicious = len(suspicious_reasons) > 0
        
        if suspicious_reasons:
            errors.append(f"Suspicious: {', '.join(suspicious_reasons)}")
        
        return ComprehensiveAddressReport(
            address=address,
            normalized_address=normalized,
            format_valid=format_valid,
            checksum_valid=checksum_valid,
            is_zero_address=zero_address,
            exists_on_chain=on_chain_result.exists,
            is_contract=on_chain_result.is_contract,
            balance_eth=on_chain_result.balance_eth,
            transaction_count=on_chain_result.transaction_count,
            address_age_days=on_chain_result.address_age_days,
            first_activity_date=on_chain_result.first_tx_date,
            is_new_address=is_new,
            is_dormant=is_dormant,
            is_suspicious=is_suspicious,
            verification_timestamp=datetime.now().isoformat(),
            errors="; ".join(errors) if errors else None
        )
    
    def quick_check(self, address: str) -> Dict[str, Any]:
        """
        Quick address check returning essential info only.
        
        Args:
            address: Ethereum address to check
            
        Returns:
            Dictionary with essential verification info
        """
        format_valid = is_valid_eth_address_format(address)
        
        if not format_valid:
            return {
                "address": address,
                "valid": False,
                "exists": False,
                "reason": "Invalid address format"
            }
        
        exists = self.collector.address_exists(address)
        is_contract, _ = self.collector.is_contract(address)
        
        return {
            "address": normalize_address(address),
            "valid": True,
            "exists": exists,
            "is_contract": is_contract,
            "reason": None
        }
    
    def is_trusted_address(self, address: str, min_age_days: int = 90, min_tx_count: int = 10) -> bool:
        """
        Check if an address meets trust criteria.
        
        Trust criteria:
        - Valid format
        - Exists on-chain
        - Not a zero address
        - Minimum age (default 90 days)
        - Minimum transaction count (default 10)
        
        Args:
            address: Address to check
            min_age_days: Minimum address age in days
            min_tx_count: Minimum transaction count
            
        Returns:
            True if address meets all trust criteria
        """
        if not is_valid_eth_address_format(address):
            return False
        
        if is_zero_address(address):
            return False
        
        result = self.collector.verify_address(address)
        
        if not result.exists:
            return False
        
        if result.address_age_days is None or result.address_age_days < min_age_days:
            return False
        
        if result.transaction_count < min_tx_count:
            return False
        
        return True


if __name__ == "__main__":
    # Example usage
    verifier = AddressVerifier()
    
    # Test with a known address
    test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    print(f"Verifying: {test_address}\n")
    
    report = verifier.verify(test_address)
    print(f"Format Valid: {report.format_valid}")
    print(f"Exists On-Chain: {report.exists_on_chain}")
    print(f"Is Contract: {report.is_contract}")
    print(f"Balance: {report.balance_eth:.4f} ETH")
    print(f"Transaction Count: {report.transaction_count}")
    print(f"Address Age: {report.address_age_days} days")
    print(f"Is Suspicious: {report.is_suspicious}")
