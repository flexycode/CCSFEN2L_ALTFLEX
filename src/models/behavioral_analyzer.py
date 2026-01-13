"""
Behavioral Analyzer Module.

High-level behavioral analysis for detecting suspicious address patterns.
Combines transaction velocity scoring, funding source analysis, and reputation scoring.

Part of Phase 2 Security Enhancement (Sprint 3).
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class VelocityScore:
    """Transaction velocity analysis result."""
    address: str
    tx_count_1h: int
    tx_count_24h: int
    tx_count_7d: int
    avg_tx_per_day: float
    max_tx_in_hour: int
    burst_detected: bool
    velocity_risk_score: float  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FundingPatternScore:
    """Funding source pattern analysis result."""
    address: str
    unique_funding_sources: int
    primary_funding_source: Optional[str]
    funding_concentration: float  # 0-1, higher = more concentrated
    circular_funding_detected: bool
    wash_trading_indicators: int
    funding_risk_score: float  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BehavioralReport:
    """Complete behavioral analysis report for an address."""
    address: str
    velocity_score: VelocityScore
    funding_pattern: FundingPatternScore
    
    # Aggregate scores
    overall_risk_score: float  # 0-1
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
    suspicious_patterns: List[str]
    
    # Metadata
    analysis_timestamp: str
    tx_analyzed: int
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['velocity_score'] = self.velocity_score.to_dict()
        result['funding_pattern'] = self.funding_pattern.to_dict()
        return result


class BehavioralAnalyzer:
    """
    Behavioral analysis engine for detecting suspicious address patterns.
    
    Analyzes:
    - Transaction velocity and burst patterns
    - Funding source diversity and concentration
    - Circular funding / wash trading indicators
    - Sybil attack patterns
    """
    
    # Thresholds for risk detection
    BURST_TX_THRESHOLD = 10  # Transactions per hour to flag as burst
    HIGH_VELOCITY_THRESHOLD = 50  # Transactions per day
    MIN_FUNDING_DIVERSITY = 3  # Minimum different funding sources
    CONCENTRATION_THRESHOLD = 0.8  # 80% from single source is suspicious
    
    def __init__(self):
        """Initialize the behavioral analyzer."""
        self.known_exchange_addresses: Set[str] = self._load_exchange_addresses()
        self.known_mixer_addresses: Set[str] = self._load_mixer_addresses()
    
    def _load_exchange_addresses(self) -> Set[str]:
        """Load known exchange addresses (simplified list)."""
        # In production, this would load from a database or API
        return {
            "0x28c6c06298d514db089934071355e5743bf21d60",  # Binance Hot Wallet
            "0x21a31ee1afc51d94c2efccaa2092ad1028285549",  # Binance
            "0xdfd5293d8e347dfe59e90efd55b2956a1343963d",  # Coinbase
            "0x71660c4005ba85c37ccec55d0c4493e66fe775d3",  # Coinbase
        }
    
    def _load_mixer_addresses(self) -> Set[str]:
        """Load known mixer/tumbler addresses."""
        return {
            "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b",  # Tornado Cash
            "0x722122df12d4e14e13ac3b6895a86e84145b6967",  # Tornado Cash Router
        }
    
    def analyze_velocity(
        self, 
        transactions: pd.DataFrame, 
        address: str,
        reference_time: Optional[datetime] = None
    ) -> VelocityScore:
        """
        Analyze transaction velocity patterns for an address.
        
        Args:
            transactions: DataFrame with transaction history
            address: Address to analyze
            reference_time: Reference point for time windows (default: now)
            
        Returns:
            VelocityScore with velocity metrics and risk assessment
        """
        if reference_time is None:
            reference_time = datetime.now()
        
        addr_lower = address.lower()
        
        # Filter transactions for this address
        mask = (transactions['from_address'].str.lower() == addr_lower) | \
               (transactions['to_address'].str.lower() == addr_lower)
        addr_txs = transactions[mask].copy()
        
        if len(addr_txs) == 0:
            return self._empty_velocity_score(address)
        
        # Convert timestamp to datetime
        addr_txs['datetime'] = pd.to_datetime(addr_txs['timestamp'], unit='s')
        
        # Calculate time windows
        one_hour_ago = reference_time - timedelta(hours=1)
        one_day_ago = reference_time - timedelta(days=1)
        seven_days_ago = reference_time - timedelta(days=7)
        
        # Count transactions in windows
        tx_1h = len(addr_txs[addr_txs['datetime'] >= one_hour_ago])
        tx_24h = len(addr_txs[addr_txs['datetime'] >= one_day_ago])
        tx_7d = len(addr_txs[addr_txs['datetime'] >= seven_days_ago])
        
        # Calculate average transactions per day
        if len(addr_txs) > 1:
            time_span = (addr_txs['datetime'].max() - addr_txs['datetime'].min()).total_seconds()
            days_active = max(time_span / 86400, 1)
            avg_per_day = len(addr_txs) / days_active
        else:
            avg_per_day = len(addr_txs)
        
        # Find maximum transactions in any single hour
        addr_txs['hour_bucket'] = addr_txs['datetime'].dt.floor('H')
        hourly_counts = addr_txs.groupby('hour_bucket').size()
        max_tx_hour = hourly_counts.max() if len(hourly_counts) > 0 else 0
        
        # Detect burst activity
        burst_detected = max_tx_hour >= self.BURST_TX_THRESHOLD
        
        # Calculate velocity risk score (0-1)
        velocity_risk = min(1.0, (
            (tx_1h / self.BURST_TX_THRESHOLD) * 0.4 +
            (avg_per_day / self.HIGH_VELOCITY_THRESHOLD) * 0.3 +
            (1.0 if burst_detected else 0.0) * 0.3
        ))
        
        return VelocityScore(
            address=addr_lower,
            tx_count_1h=tx_1h,
            tx_count_24h=tx_24h,
            tx_count_7d=tx_7d,
            avg_tx_per_day=round(avg_per_day, 2),
            max_tx_in_hour=max_tx_hour,
            burst_detected=burst_detected,
            velocity_risk_score=round(velocity_risk, 3)
        )
    
    def analyze_funding_patterns(
        self, 
        transactions: pd.DataFrame, 
        address: str
    ) -> FundingPatternScore:
        """
        Analyze funding source patterns for an address.
        
        Args:
            transactions: DataFrame with transaction history
            address: Address to analyze
            
        Returns:
            FundingPatternScore with funding pattern metrics
        """
        addr_lower = address.lower()
        
        # Get incoming transactions (where address is recipient)
        incoming = transactions[transactions['to_address'].str.lower() == addr_lower].copy()
        outgoing = transactions[transactions['from_address'].str.lower() == addr_lower].copy()
        
        if len(incoming) == 0:
            return self._empty_funding_score(address)
        
        # Analyze funding sources
        funding_sources = incoming['from_address'].str.lower().value_counts()
        unique_sources = len(funding_sources)
        
        # Primary funding source
        primary_source = funding_sources.index[0] if len(funding_sources) > 0 else None
        
        # Funding concentration (what % comes from top source)
        total_incoming = len(incoming)
        concentration = funding_sources.iloc[0] / total_incoming if total_incoming > 0 else 0
        
        # Detect circular funding (money sent to addresses that later fund this address)
        outgoing_recipients = set(outgoing['to_address'].str.lower())
        circular_sources = set(funding_sources.index) & outgoing_recipients
        circular_detected = len(circular_sources) > 0
        
        # Wash trading indicators
        wash_indicators = 0
        
        # 1. High concentration from single source
        if concentration > self.CONCENTRATION_THRESHOLD:
            wash_indicators += 1
        
        # 2. Low funding diversity
        if unique_sources < self.MIN_FUNDING_DIVERSITY:
            wash_indicators += 1
        
        # 3. Circular funding detected
        if circular_detected:
            wash_indicators += 2
        
        # 4. Funding from known mixers
        mixer_funding = set(funding_sources.index) & self.known_mixer_addresses
        if len(mixer_funding) > 0:
            wash_indicators += 2
        
        # Calculate funding risk score
        funding_risk = min(1.0, (
            concentration * 0.3 +
            (1.0 if circular_detected else 0.0) * 0.3 +
            (wash_indicators / 6) * 0.4
        ))
        
        return FundingPatternScore(
            address=addr_lower,
            unique_funding_sources=unique_sources,
            primary_funding_source=primary_source,
            funding_concentration=round(concentration, 3),
            circular_funding_detected=circular_detected,
            wash_trading_indicators=wash_indicators,
            funding_risk_score=round(funding_risk, 3)
        )
    
    def analyze_address(
        self, 
        transactions: pd.DataFrame, 
        address: str
    ) -> BehavioralReport:
        """
        Perform comprehensive behavioral analysis on an address.
        
        Args:
            transactions: DataFrame with transaction history
            address: Address to analyze
            
        Returns:
            BehavioralReport with complete analysis
        """
        # Get individual scores
        velocity = self.analyze_velocity(transactions, address)
        funding = self.analyze_funding_patterns(transactions, address)
        
        # Identify suspicious patterns
        suspicious_patterns = []
        
        if velocity.burst_detected:
            suspicious_patterns.append("Burst transaction activity detected")
        
        if velocity.avg_tx_per_day > self.HIGH_VELOCITY_THRESHOLD:
            suspicious_patterns.append("Unusually high transaction velocity")
        
        if funding.circular_funding_detected:
            suspicious_patterns.append("Circular funding pattern detected")
        
        if funding.funding_concentration > self.CONCENTRATION_THRESHOLD:
            suspicious_patterns.append("High funding concentration from single source")
        
        if funding.wash_trading_indicators >= 3:
            suspicious_patterns.append("Multiple wash trading indicators")
        
        # Calculate overall risk score
        overall_risk = (velocity.velocity_risk_score * 0.4 + 
                       funding.funding_risk_score * 0.6)
        
        # Determine risk level
        risk_level = self._get_risk_level(overall_risk)
        
        # Count analyzed transactions
        addr_lower = address.lower()
        mask = (transactions['from_address'].str.lower() == addr_lower) | \
               (transactions['to_address'].str.lower() == addr_lower)
        tx_count = mask.sum()
        
        return BehavioralReport(
            address=addr_lower,
            velocity_score=velocity,
            funding_pattern=funding,
            overall_risk_score=round(overall_risk, 3),
            risk_level=risk_level,
            suspicious_patterns=suspicious_patterns,
            analysis_timestamp=datetime.now().isoformat(),
            tx_analyzed=tx_count
        )
    
    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to human-readable level."""
        if score >= 0.8:
            return "CRITICAL"
        elif score >= 0.6:
            return "HIGH"
        elif score >= 0.4:
            return "MEDIUM"
        elif score >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _empty_velocity_score(self, address: str) -> VelocityScore:
        """Return empty velocity score for address with no transactions."""
        return VelocityScore(
            address=address.lower(),
            tx_count_1h=0,
            tx_count_24h=0,
            tx_count_7d=0,
            avg_tx_per_day=0.0,
            max_tx_in_hour=0,
            burst_detected=False,
            velocity_risk_score=0.0
        )
    
    def _empty_funding_score(self, address: str) -> FundingPatternScore:
        """Return empty funding score for address with no incoming transactions."""
        return FundingPatternScore(
            address=address.lower(),
            unique_funding_sources=0,
            primary_funding_source=None,
            funding_concentration=0.0,
            circular_funding_detected=False,
            wash_trading_indicators=0,
            funding_risk_score=0.0
        )
    
    def batch_analyze(
        self, 
        transactions: pd.DataFrame, 
        addresses: List[str]
    ) -> Dict[str, BehavioralReport]:
        """
        Analyze multiple addresses in batch.
        
        Args:
            transactions: DataFrame with transaction history
            addresses: List of addresses to analyze
            
        Returns:
            Dictionary mapping addresses to their BehavioralReports
        """
        return {addr: self.analyze_address(transactions, addr) for addr in addresses}


if __name__ == "__main__":
    # Demo
    analyzer = BehavioralAnalyzer()
    print("Behavioral Analyzer initialized.")
    print(f"Known exchange addresses: {len(analyzer.known_exchange_addresses)}")
    print(f"Known mixer addresses: {len(analyzer.known_mixer_addresses)}")
