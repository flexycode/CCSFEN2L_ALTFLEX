"""
Unit tests for AltFlex detection modules.
"""

import pytest
import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.feature_engineer import FeatureEngineer
from src.models.anomaly_detector import AnomalyDetector
from src.forensics.exploit_detector import ExploitDetector


# =============================================================================
# Feature Engineer Tests
# =============================================================================

class TestFeatureEngineer:
    """Tests for the FeatureEngineer class."""
    
    @pytest.fixture
    def engineer(self):
        return FeatureEngineer()
    
    @pytest.fixture
    def sample_df(self):
        """Create sample transaction data."""
        return pd.DataFrame({
            'tx_hash': ['0x123', '0x456', '0x789'],
            'block_number': [1000, 1000, 1001],
            'timestamp': [1697500000, 1697500000, 1697500012],
            'from_address': ['0xabc', '0xdef', '0xghi'],
            'to_address': ['0x111', '0x222', '0x333'],
            'value_eth': [1.0, 150.0, 5.0],
            'gas_used': [100000, 600000, 200000],
            'gas_price_gwei': [25, 100, 30],
            'is_flash_loan': [False, True, False],
            'is_malicious': [False, True, False]
        })
    
    def test_initialization(self, engineer):
        """Test FeatureEngineer initialization."""
        assert engineer is not None
        assert engineer.LARGE_VALUE_THRESHOLD_ETH == 100
    
    def test_process_transaction_data(self, engineer, sample_df):
        """Test feature extraction from transactions."""
        features = engineer.process_transaction_data(sample_df)
        
        assert features is not None
        assert len(features) == len(sample_df)
        assert 'value_eth' in features.columns
        assert 'is_large_value' in features.columns
        assert 'is_high_gas' in features.columns
        assert 'log_value' in features.columns
    
    def test_large_value_detection(self, engineer, sample_df):
        """Test detection of large value transactions."""
        features = engineer.process_transaction_data(sample_df)
        
        # Second transaction has 150 ETH (above threshold)
        assert features.iloc[1]['is_large_value'] == 1
        # First transaction has 1 ETH (below threshold)
        assert features.iloc[0]['is_large_value'] == 0
    
    def test_high_gas_detection(self, engineer, sample_df):
        """Test detection of high gas usage."""
        features = engineer.process_transaction_data(sample_df)
        
        # Second transaction has 600k gas (above threshold)
        assert features.iloc[1]['is_high_gas'] == 1
        # First transaction has 100k gas (below threshold)
        assert features.iloc[0]['is_high_gas'] == 0
    
    def test_address_features(self, engineer, sample_df):
        """Test address-level feature extraction."""
        features = engineer.extract_address_features(sample_df, '0xabc')
        
        assert features['tx_count'] == 1
        assert features['total_value_eth'] == 1.0
    
    def test_empty_address_features(self, engineer, sample_df):
        """Test features for non-existent address."""
        features = engineer.extract_address_features(sample_df, '0xnonexistent')
        
        assert features['tx_count'] == 0
        assert features['total_value_eth'] == 0.0
    
    def test_prepare_training_data(self, engineer, sample_df):
        """Test training data preparation."""
        X, y, feature_names = engineer.prepare_training_data(sample_df)
        
        assert X is not None
        assert y is not None
        assert len(X) == len(sample_df)
        assert len(y) == len(sample_df)
        assert len(feature_names) > 0


# =============================================================================
# Anomaly Detector Tests
# =============================================================================

class TestAnomalyDetector:
    """Tests for the AnomalyDetector class."""
    
    @pytest.fixture
    def detector(self):
        return AnomalyDetector()
    
    @pytest.fixture
    def training_data(self):
        """Create training data."""
        np.random.seed(42)
        n_samples = 100
        
        # Normal transactions
        X_normal = np.random.rand(n_samples // 2, 5) * 10
        y_normal = np.zeros(n_samples // 2)
        
        # Malicious transactions (higher values)
        X_malicious = np.random.rand(n_samples // 2, 5) * 10 + 50
        y_malicious = np.ones(n_samples // 2)
        
        X = np.vstack([X_normal, X_malicious])
        y = np.hstack([y_normal, y_malicious])
        
        return X, y
    
    def test_initialization(self, detector):
        """Test AnomalyDetector initialization."""
        assert detector is not None
        assert detector.is_trained == False
    
    def test_train(self, detector, training_data):
        """Test model training."""
        X, y = training_data
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        stats = detector.train(X, y, feature_names)
        
        assert detector.is_trained == True
        assert 'val_accuracy' in stats
        assert stats['val_accuracy'] > 0.5  # Should be better than random
    
    def test_predict(self, detector, training_data):
        """Test prediction after training."""
        X, y = training_data
        detector.train(X, y)
        
        predictions = detector.predict(X[:5])
        
        assert predictions is not None
        assert len(predictions) == 5
        assert all(p in [0, 1] for p in predictions)
    
    def test_predict_proba(self, detector, training_data):
        """Test probability prediction."""
        X, y = training_data
        detector.train(X, y)
        
        probas = detector.predict_proba(X[:5])
        
        assert probas is not None
        assert probas.shape == (5, 2)
        assert all(0 <= p <= 1 for p in probas.flatten())
    
    def test_detect(self, detector, training_data):
        """Test full detection pipeline."""
        X, y = training_data
        detector.train(X, y)
        
        results = detector.detect(X[:3])
        
        assert len(results) == 3
        assert all('is_malicious' in r for r in results)
        assert all('confidence' in r for r in results)
        assert all('risk_level' in r for r in results)
    
    def test_feature_importance(self, detector, training_data):
        """Test feature importance extraction."""
        X, y = training_data
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        detector.train(X, y, feature_names)
        
        importance = detector.get_feature_importance()
        
        assert len(importance) == len(feature_names)
        assert all(v >= 0 for v in importance.values())
    
    def test_model_info(self, detector, training_data):
        """Test model info retrieval."""
        X, y = training_data
        detector.train(X, y)
        
        info = detector.get_model_info()
        
        assert info['is_trained'] == True
        assert info['model_type'] == 'XGBClassifier'


# =============================================================================
# Exploit Detector Tests
# =============================================================================

class TestExploitDetector:
    """Tests for the ExploitDetector class."""
    
    @pytest.fixture
    def detector(self):
        return ExploitDetector()
    
    @pytest.fixture
    def normal_tx(self):
        """Normal transaction data."""
        return {
            'tx_hash': '0x123',
            'from_address': '0xabc123',
            'to_address': '0xdef456',
            'value_eth': 1.5,
            'gas_used': 100000,
            'gas_price_gwei': 25,
            'is_flash_loan': False
        }
    
    @pytest.fixture
    def suspicious_tx(self):
        """Suspicious transaction data."""
        return {
            'tx_hash': '0x456',
            'from_address': '0xb66cd966670d962C227B3EABA30a872DbFb995db',  # Known attacker
            'to_address': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',
            'value_eth': 5000,
            'gas_used': 2000000,
            'gas_price_gwei': 150,
            'is_flash_loan': True,
            'is_malicious': True
        }
    
    def test_initialization(self, detector):
        """Test ExploitDetector initialization."""
        assert detector is not None
        assert len(detector.known_attacker_addresses) > 0
    
    def test_known_attacker_detection(self, detector):
        """Test detection of known attacker address."""
        # Known Euler attacker
        result = detector.check_address("0xb66cd966670d962C227B3EABA30a872DbFb995db")
        
        assert result['is_known_attacker'] == True
        assert result['exploit_info'] is not None
        assert 'Euler' in result['exploit_info']['name']
    
    def test_unknown_address(self, detector):
        """Test check for unknown address."""
        result = detector.check_address("0x1234567890abcdef1234567890abcdef12345678")
        
        assert result['is_known_attacker'] == False
        assert result['exploit_info'] is None
    
    def test_detect_all_normal(self, detector, normal_tx):
        """Test detection on normal transaction."""
        results = detector.detect_all(normal_tx)
        
        assert len(results) == 6  # 6 detection rules
        
        # Most rules should not trigger for normal tx
        triggered = [r for r in results if r.is_triggered]
        assert len(triggered) < 3
    
    def test_detect_all_suspicious(self, detector, suspicious_tx):
        """Test detection on suspicious transaction."""
        results = detector.detect_all(suspicious_tx)
        
        # Multiple rules should trigger for suspicious tx
        triggered = [r for r in results if r.is_triggered]
        assert len(triggered) >= 3
    
    def test_analyze_normal(self, detector, normal_tx):
        """Test full analysis on normal transaction."""
        result = detector.analyze(normal_tx)
        
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert result['risk_score'] < 0.5  # Should be low risk
    
    def test_analyze_suspicious(self, detector, suspicious_tx):
        """Test full analysis on suspicious transaction."""
        result = detector.analyze(suspicious_tx)
        
        assert result['is_suspicious'] == True
        assert result['risk_score'] >= 0.4
    
    def test_get_known_exploits(self, detector):
        """Test retrieval of known exploits."""
        exploits = detector.get_known_exploits()
        
        assert len(exploits) > 0
        assert all('name' in e for e in exploits)
        assert all('loss_usd' in e for e in exploits)
    
    def test_get_detection_rules(self, detector):
        """Test retrieval of detection rules."""
        rules = detector.get_detection_rules()
        
        assert 'flash_loan_indicators' in rules or 'suspicious_functions' in rules


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
