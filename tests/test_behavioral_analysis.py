"""
Unit Tests for Behavioral Analysis.

Tests for Sprint 3: Behavioral Analysis Enhancement.

Covers velocity scoring, funding pattern analysis, and blacklist integration.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.behavioral_analyzer import (
    BehavioralAnalyzer,
    VelocityScore,
    FundingPatternScore,
    BehavioralReport,
)
from models.feature_engineer import FeatureEngineer
from forensics.exploit_detector import ExploitDetector


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_transactions():
    """Create sample transaction DataFrame."""
    base_time = int(datetime.now().timestamp()) - 86400  # 24 hours ago
    
    return pd.DataFrame({
        'tx_hash': [f'0x{i:064x}' for i in range(20)],
        'block_number': [1000 + i for i in range(20)],
        'timestamp': [base_time + i * 3600 for i in range(20)],  # 1 tx per hour
        'from_address': ['0xabc123'] * 10 + ['0xdef456'] * 5 + ['0xghi789'] * 5,
        'to_address': ['0xdef456'] * 5 + ['0xabc123'] * 10 + ['0xabc123'] * 5,
        'value_eth': [1.0] * 10 + [5.0] * 5 + [2.0] * 5,
        'gas_used': [100000] * 20,
        'gas_price_gwei': [25] * 20,
        'is_flash_loan': [False] * 20,
    })


@pytest.fixture
def high_velocity_transactions():
    """Create high velocity transaction DataFrame (many tx in short time)."""
    base_time = int(datetime.now().timestamp()) - 3600  # 1 hour ago
    
    return pd.DataFrame({
        'tx_hash': [f'0x{i:064x}' for i in range(50)],
        'block_number': [1000 + i for i in range(50)],
        'timestamp': [base_time + i * 60 for i in range(50)],  # 1 tx per minute
        'from_address': ['0xhigh_velocity'] * 50,
        'to_address': ['0xtarget'] * 50,
        'value_eth': [0.5] * 50,
        'gas_used': [100000] * 50,
        'gas_price_gwei': [25] * 50,
        'is_flash_loan': [False] * 50,
    })


@pytest.fixture
def circular_funding_transactions():
    """Create transactions with circular funding pattern."""
    base_time = int(datetime.now().timestamp()) - 86400
    
    return pd.DataFrame({
        'tx_hash': [f'0x{i:064x}' for i in range(10)],
        'block_number': [1000 + i for i in range(10)],
        'timestamp': [base_time + i * 3600 for i in range(10)],
        'from_address': ['0xA', '0xB', '0xA', '0xB', '0xC', '0xA', '0xB', '0xA', '0xC', '0xA'],
        'to_address': ['0xB', '0xA', '0xB', '0xA', '0xA', '0xB', '0xA', '0xC', '0xB', '0xB'],
        'value_eth': [10.0] * 10,
        'gas_used': [100000] * 10,
        'gas_price_gwei': [25] * 10,
        'is_flash_loan': [False] * 10,
    })


# =============================================================================
# BehavioralAnalyzer Tests
# =============================================================================

class TestBehavioralAnalyzer:
    """Tests for BehavioralAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        return BehavioralAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer is not None
        assert len(analyzer.known_exchange_addresses) > 0
        assert len(analyzer.known_mixer_addresses) > 0
    
    def test_thresholds(self, analyzer):
        """Test threshold constants are defined."""
        assert analyzer.BURST_TX_THRESHOLD > 0
        assert analyzer.HIGH_VELOCITY_THRESHOLD > 0
        assert analyzer.MIN_FUNDING_DIVERSITY > 0
        assert 0 < analyzer.CONCENTRATION_THRESHOLD <= 1


class TestVelocityAnalysis:
    """Tests for velocity scoring."""
    
    @pytest.fixture
    def analyzer(self):
        return BehavioralAnalyzer()
    
    def test_normal_velocity(self, analyzer, sample_transactions):
        """Test velocity analysis with normal transaction pattern."""
        result = analyzer.analyze_velocity(sample_transactions, '0xabc123')
        
        assert isinstance(result, VelocityScore)
        assert result.address == '0xabc123'
        assert result.burst_detected == False  # Use == instead of 'is' for numpy compatibility
        assert 0 <= result.velocity_risk_score <= 1
    
    def test_high_velocity(self, analyzer, high_velocity_transactions):
        """Test velocity analysis with high transaction frequency."""
        result = analyzer.analyze_velocity(high_velocity_transactions, '0xhigh_velocity')
        
        assert result.avg_tx_per_day > 10
        assert result.max_tx_in_hour >= 10
        assert result.velocity_risk_score > 0.5
    
    def test_empty_address(self, analyzer, sample_transactions):
        """Test velocity analysis for address with no transactions."""
        result = analyzer.analyze_velocity(sample_transactions, '0xnonexistent')
        
        assert result.tx_count_1h == 0
        assert result.tx_count_24h == 0
        assert result.velocity_risk_score == 0.0
    
    def test_velocity_score_to_dict(self, analyzer, sample_transactions):
        """Test VelocityScore serialization."""
        result = analyzer.analyze_velocity(sample_transactions, '0xabc123')
        result_dict = result.to_dict()
        
        assert 'address' in result_dict
        assert 'velocity_risk_score' in result_dict
        assert 'burst_detected' in result_dict


class TestFundingPatternAnalysis:
    """Tests for funding pattern scoring."""
    
    @pytest.fixture
    def analyzer(self):
        return BehavioralAnalyzer()
    
    def test_normal_funding(self, analyzer, sample_transactions):
        """Test funding analysis with normal pattern."""
        result = analyzer.analyze_funding_patterns(sample_transactions, '0xabc123')
        
        assert isinstance(result, FundingPatternScore)
        assert result.unique_funding_sources > 0
        assert 0 <= result.funding_concentration <= 1
    
    def test_circular_funding_detection(self, analyzer, circular_funding_transactions):
        """Test detection of circular funding patterns."""
        result = analyzer.analyze_funding_patterns(circular_funding_transactions, '0xA')
        
        # Address 0xA receives from 0xB and 0xC, and sends to 0xB - circular!
        assert result.circular_funding_detected is True
        assert result.wash_trading_indicators >= 1
    
    def test_highly_concentrated_funding(self, analyzer):
        """Test detection of highly concentrated funding."""
        # Create transactions where one address funds all
        base_time = int(datetime.now().timestamp()) - 86400
        concentrated_txs = pd.DataFrame({
            'tx_hash': [f'0x{i:064x}' for i in range(10)],
            'block_number': [1000 + i for i in range(10)],
            'timestamp': [base_time + i * 3600 for i in range(10)],
            'from_address': ['0xsingle_source'] * 10,
            'to_address': ['0xtarget'] * 10,
            'value_eth': [1.0] * 10,
            'gas_used': [100000] * 10,
            'gas_price_gwei': [25] * 10,
            'is_flash_loan': [False] * 10,
        })
        
        result = analyzer.analyze_funding_patterns(concentrated_txs, '0xtarget')
        
        assert result.funding_concentration == 1.0  # 100% from single source
        assert result.unique_funding_sources == 1
    
    def test_no_incoming_transactions(self, analyzer, sample_transactions):
        """Test funding analysis for address with no incoming transactions."""
        result = analyzer.analyze_funding_patterns(sample_transactions, '0xnonexistent')
        
        assert result.unique_funding_sources == 0
        assert result.funding_risk_score == 0.0


class TestComprehensiveAnalysis:
    """Tests for complete behavioral analysis."""
    
    @pytest.fixture
    def analyzer(self):
        return BehavioralAnalyzer()
    
    def test_analyze_address(self, analyzer, sample_transactions):
        """Test comprehensive address analysis."""
        result = analyzer.analyze_address(sample_transactions, '0xabc123')
        
        assert isinstance(result, BehavioralReport)
        assert result.address == '0xabc123'
        assert isinstance(result.velocity_score, VelocityScore)
        assert isinstance(result.funding_pattern, FundingPatternScore)
        assert 0 <= result.overall_risk_score <= 1
        assert result.risk_level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'MINIMAL']
    
    def test_suspicious_patterns_list(self, analyzer, circular_funding_transactions):
        """Test that suspicious patterns are identified."""
        result = analyzer.analyze_address(circular_funding_transactions, '0xA')
        
        assert isinstance(result.suspicious_patterns, list)
        # Should have at least circular funding pattern
        assert len(result.suspicious_patterns) >= 1
    
    def test_report_to_dict(self, analyzer, sample_transactions):
        """Test BehavioralReport serialization."""
        result = analyzer.analyze_address(sample_transactions, '0xabc123')
        result_dict = result.to_dict()
        
        assert 'address' in result_dict
        assert 'velocity_score' in result_dict
        assert 'funding_pattern' in result_dict
        assert 'overall_risk_score' in result_dict
    
    def test_batch_analyze(self, analyzer, sample_transactions):
        """Test batch analysis of multiple addresses."""
        addresses = ['0xabc123', '0xdef456', '0xghi789']
        results = analyzer.batch_analyze(sample_transactions, addresses)
        
        assert len(results) == 3
        assert all(addr in results for addr in addresses)
        assert all(isinstance(r, BehavioralReport) for r in results.values())


# =============================================================================
# FeatureEngineer Velocity/Funding Tests
# =============================================================================

class TestFeatureEngineerEnhanced:
    """Tests for enhanced FeatureEngineer methods."""
    
    @pytest.fixture
    def engineer(self):
        return FeatureEngineer()
    
    def test_compute_velocity_features(self, engineer, sample_transactions):
        """Test velocity feature computation."""
        result = engineer.compute_velocity_features(sample_transactions, '0xabc123')
        
        assert 'velocity_tx_per_day' in result
        assert 'velocity_max_hourly' in result
        assert 'velocity_burst_count' in result
        assert 'velocity_score' in result
        assert 0 <= result['velocity_score'] <= 1
    
    def test_compute_funding_pattern_features(self, engineer, sample_transactions):
        """Test funding pattern feature computation."""
        result = engineer.compute_funding_pattern_features(sample_transactions, '0xabc123')
        
        assert 'funding_source_count' in result
        assert 'funding_concentration' in result
        assert 'circular_funding_flag' in result
        assert 'funding_diversity_score' in result
    
    def test_extract_enhanced_address_features(self, engineer, sample_transactions):
        """Test enhanced address feature extraction."""
        result = engineer.extract_enhanced_address_features(sample_transactions, '0xabc123')
        
        # Should include base features
        assert 'tx_count' in result
        assert 'total_value_eth' in result
        
        # Should include velocity features
        assert 'velocity_tx_per_day' in result
        
        # Should include funding features
        assert 'funding_source_count' in result
        
        # Should include composite score
        assert 'behavioral_risk_score' in result


# =============================================================================
# ExploitDetector Blacklist Tests
# =============================================================================

class TestExploitDetectorBlacklists:
    """Tests for external blacklist integration."""
    
    @pytest.fixture
    def detector(self):
        return ExploitDetector()
    
    def test_ofac_addresses_loaded(self, detector):
        """Test OFAC addresses are loaded."""
        ofac = detector._get_ofac_addresses()
        assert len(ofac) > 0
        assert all(addr.startswith('0x') for addr in ofac)
    
    def test_mixer_addresses_loaded(self, detector):
        """Test mixer addresses are loaded."""
        mixers = detector._get_mixer_addresses()
        assert len(mixers) > 0
    
    def test_check_external_blacklists_clean(self, detector):
        """Test blacklist check for clean address."""
        result = detector.check_external_blacklists('0x1234567890abcdef1234567890abcdef12345678')
        
        assert result['is_blacklisted'] is False
        assert result['severity'] == 'NONE'
        assert result['risk_category'] is None
    
    def test_check_external_blacklists_ofac(self, detector):
        """Test blacklist check for OFAC sanctioned address."""
        # Use a known OFAC address from the list
        ofac_addr = "0x722122df12d4e14e13ac3b6895a86e84145b6967"
        result = detector.check_external_blacklists(ofac_addr)
        
        assert result['is_blacklisted'] is True
        assert result['severity'] == 'CRITICAL'
        assert result['blacklist_matches']['ofac_sanctioned'] is True
    
    def test_check_external_blacklists_mixer(self, detector):
        """Test blacklist check for mixer address."""
        mixer_addr = "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b"
        result = detector.check_external_blacklists(mixer_addr)
        
        assert result['is_blacklisted'] is True
        assert result['blacklist_matches']['known_mixers'] is True
    
    def test_comprehensive_address_risk_clean(self, detector):
        """Test comprehensive risk for clean address."""
        result = detector.get_comprehensive_address_risk('0x1234567890abcdef1234567890abcdef12345678')
        
        assert result['is_high_risk'] is False
        assert result['overall_severity'] == 'NONE'
        assert 'internal_check' in result
        assert 'external_check' in result
    
    def test_comprehensive_address_risk_attacker(self, detector):
        """Test comprehensive risk for known attacker."""
        # Use Euler attacker address
        result = detector.get_comprehensive_address_risk('0xb66cd966670d962C227B3EABA30a872DbFb995db')
        
        assert result['is_high_risk'] is True
        assert result['overall_severity'] == 'CRITICAL'
        assert result['internal_check']['is_known_attacker'] is True


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
