"""
Feature Engineering Module.

This module handles the transformation of raw blockchain data into features suitable for ML models.
Specifically designed for flash loan attack detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime


class FeatureEngineer:
    """
    Feature extraction pipeline for blockchain transaction analysis.
    Focuses on flash loan attack indicators.
    """
    
    # Thresholds for feature engineering
    LARGE_VALUE_THRESHOLD_ETH = 100  # ETH
    HIGH_GAS_THRESHOLD = 500000
    HIGH_GAS_PRICE_GWEI = 50
    RAPID_TX_WINDOW_SECONDS = 60
    
    def __init__(self):
        self.feature_names = []
    
    def process_transaction_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts features from transaction dataframe.
        
        Args:
            raw_data: DataFrame with columns: tx_hash, block_number, timestamp, 
                     from_address, to_address, value_eth, gas_used, gas_price_gwei
        
        Returns:
            DataFrame with extracted features
        """
        df = raw_data.copy()
        
        # Basic features
        features = pd.DataFrame()
        features['value_eth'] = df['value_eth'].astype(float)
        features['gas_used'] = df['gas_used'].astype(float)
        features['gas_price_gwei'] = df['gas_price_gwei'].astype(float)
        
        # Calculated features
        features['gas_cost_eth'] = (features['gas_used'] * features['gas_price_gwei']) / 1e9
        features['value_to_gas_ratio'] = features['value_eth'] / (features['gas_cost_eth'] + 1e-10)
        
        # Binary indicator features
        features['is_large_value'] = (features['value_eth'] > self.LARGE_VALUE_THRESHOLD_ETH).astype(int)
        features['is_high_gas'] = (features['gas_used'] > self.HIGH_GAS_THRESHOLD).astype(int)
        features['is_high_gas_price'] = (features['gas_price_gwei'] > self.HIGH_GAS_PRICE_GWEI).astype(int)
        
        # Flash loan indicator if column exists
        if 'is_flash_loan' in df.columns:
            features['is_flash_loan'] = df['is_flash_loan'].astype(int)
        
        # Log transformations for better ML performance
        features['log_value'] = np.log1p(features['value_eth'])
        features['log_gas'] = np.log1p(features['gas_used'])
        
        self.feature_names = features.columns.tolist()
        return features
    
    def extract_address_features(self, transactions: pd.DataFrame, address: str) -> Dict[str, Any]:
        """
        Extract aggregate features for a specific address from its transaction history.
        
        Args:
            transactions: DataFrame of transactions
            address: The address to analyze
        
        Returns:
            Dictionary of computed features
        """
        # Filter transactions for this address
        addr_lower = address.lower()
        mask = (transactions['from_address'].str.lower() == addr_lower) | \
               (transactions['to_address'].str.lower() == addr_lower)
        addr_txs = transactions[mask].copy()
        
        if len(addr_txs) == 0:
            return self._empty_address_features()
        
        # Convert types
        addr_txs['value_eth'] = addr_txs['value_eth'].astype(float)
        addr_txs['gas_used'] = addr_txs['gas_used'].astype(float)
        addr_txs['gas_price_gwei'] = addr_txs['gas_price_gwei'].astype(float)
        addr_txs['timestamp'] = addr_txs['timestamp'].astype(int)
        
        features = {
            # Transaction count
            'tx_count': len(addr_txs),
            
            # Value statistics
            'total_value_eth': addr_txs['value_eth'].sum(),
            'mean_value_eth': addr_txs['value_eth'].mean(),
            'max_value_eth': addr_txs['value_eth'].max(),
            'std_value_eth': addr_txs['value_eth'].std() if len(addr_txs) > 1 else 0,
            
            # Gas statistics
            'mean_gas_used': addr_txs['gas_used'].mean(),
            'max_gas_used': addr_txs['gas_used'].max(),
            'mean_gas_price': addr_txs['gas_price_gwei'].mean(),
            
            # Time-based features
            'time_span_seconds': addr_txs['timestamp'].max() - addr_txs['timestamp'].min(),
            
            # Counterparty analysis
            'unique_counterparties': self._count_unique_counterparties(addr_txs, addr_lower),
            
            # Risk indicators
            'large_tx_ratio': (addr_txs['value_eth'] > self.LARGE_VALUE_THRESHOLD_ETH).mean(),
            'high_gas_tx_ratio': (addr_txs['gas_used'] > self.HIGH_GAS_THRESHOLD).mean(),
        }
        
        # Same-block transactions (flash loan indicator)
        block_counts = addr_txs['block_number'].value_counts()
        features['max_txs_same_block'] = block_counts.max() if len(block_counts) > 0 else 0
        features['has_same_block_txs'] = int(features['max_txs_same_block'] > 1)
        
        # Flash loan indicator if available
        if 'is_flash_loan' in addr_txs.columns:
            features['flash_loan_tx_count'] = addr_txs['is_flash_loan'].sum()
        else:
            features['flash_loan_tx_count'] = 0
        
        return features
    
    def _count_unique_counterparties(self, txs: pd.DataFrame, address: str) -> int:
        """Count unique addresses this address has interacted with."""
        counterparties = set()
        for _, tx in txs.iterrows():
            if tx['from_address'].lower() == address:
                counterparties.add(tx['to_address'].lower())
            else:
                counterparties.add(tx['from_address'].lower())
        return len(counterparties)
    
    def _empty_address_features(self) -> Dict[str, Any]:
        """Return empty features for an address with no transactions."""
        return {
            'tx_count': 0,
            'total_value_eth': 0.0,
            'mean_value_eth': 0.0,
            'max_value_eth': 0.0,
            'std_value_eth': 0.0,
            'mean_gas_used': 0.0,
            'max_gas_used': 0.0,
            'mean_gas_price': 0.0,
            'time_span_seconds': 0,
            'unique_counterparties': 0,
            'large_tx_ratio': 0.0,
            'high_gas_tx_ratio': 0.0,
            'max_txs_same_block': 0,
            'has_same_block_txs': 0,
            'flash_loan_tx_count': 0,
        }
    
    def compute_velocity_features(self, transactions: pd.DataFrame, address: str) -> Dict[str, Any]:
        """
        Compute transaction velocity features for an address.
        
        Sprint 3 Enhancement: ML-P2-009
        
        Args:
            transactions: DataFrame with transaction history
            address: Address to analyze
            
        Returns:
            Dictionary of velocity-based features
        """
        addr_lower = address.lower()
        mask = (transactions['from_address'].str.lower() == addr_lower) | \
               (transactions['to_address'].str.lower() == addr_lower)
        addr_txs = transactions[mask].copy()
        
        if len(addr_txs) == 0:
            return {
                'velocity_tx_per_day': 0.0,
                'velocity_max_hourly': 0,
                'velocity_burst_count': 0,
                'velocity_score': 0.0,
            }
        
        # Convert timestamp
        addr_txs['timestamp'] = addr_txs['timestamp'].astype(int)
        addr_txs['datetime'] = pd.to_datetime(addr_txs['timestamp'], unit='s')
        
        # Calculate time span
        time_span_seconds = addr_txs['timestamp'].max() - addr_txs['timestamp'].min()
        days_active = max(time_span_seconds / 86400, 1)
        tx_per_day = len(addr_txs) / days_active
        
        # Hourly buckets for burst detection
        addr_txs['hour_bucket'] = addr_txs['datetime'].dt.floor('H')
        hourly_counts = addr_txs.groupby('hour_bucket').size()
        max_hourly = hourly_counts.max() if len(hourly_counts) > 0 else 0
        
        # Count burst periods (hours with > 10 transactions)
        burst_count = (hourly_counts > 10).sum()
        
        # Velocity score (0-1)
        velocity_score = min(1.0, (tx_per_day / 50) * 0.5 + (max_hourly / 20) * 0.5)
        
        return {
            'velocity_tx_per_day': round(tx_per_day, 2),
            'velocity_max_hourly': int(max_hourly),
            'velocity_burst_count': int(burst_count),
            'velocity_score': round(velocity_score, 3),
        }
    
    def compute_funding_pattern_features(self, transactions: pd.DataFrame, address: str) -> Dict[str, Any]:
        """
        Compute funding source pattern features for an address.
        
        Sprint 3 Enhancement: ML-P2-010
        
        Args:
            transactions: DataFrame with transaction history
            address: Address to analyze
            
        Returns:
            Dictionary of funding pattern features
        """
        addr_lower = address.lower()
        
        # Incoming transactions
        incoming = transactions[transactions['to_address'].str.lower() == addr_lower]
        outgoing = transactions[transactions['from_address'].str.lower() == addr_lower]
        
        if len(incoming) == 0:
            return {
                'funding_source_count': 0,
                'funding_concentration': 0.0,
                'circular_funding_flag': 0,
                'funding_diversity_score': 0.0,
            }
        
        # Funding source analysis
        funding_sources = incoming['from_address'].str.lower().value_counts()
        source_count = len(funding_sources)
        
        # Concentration (% from top source)
        concentration = funding_sources.iloc[0] / len(incoming) if len(incoming) > 0 else 0
        
        # Circular funding detection
        outgoing_recipients = set(outgoing['to_address'].str.lower())
        circular_sources = set(funding_sources.index) & outgoing_recipients
        circular_flag = 1 if len(circular_sources) > 0 else 0
        
        # Diversity score (inverse of concentration, adjusted for source count)
        diversity = (1 - concentration) * min(1.0, source_count / 10)
        
        return {
            'funding_source_count': source_count,
            'funding_concentration': round(concentration, 3),
            'circular_funding_flag': circular_flag,
            'funding_diversity_score': round(diversity, 3),
        }
    
    def extract_enhanced_address_features(self, transactions: pd.DataFrame, address: str) -> Dict[str, Any]:
        """
        Extract comprehensive address-level features including behavioral analysis.
        
        Sprint 3 Enhancement: Combines all address intelligence.
        
        Args:
            transactions: DataFrame with transaction history
            address: Address to analyze
            
        Returns:
            Dictionary with all address-level features
        """
        # Get base features
        base_features = self.extract_address_features(transactions, address)
        
        # Add velocity features
        velocity_features = self.compute_velocity_features(transactions, address)
        
        # Add funding pattern features
        funding_features = self.compute_funding_pattern_features(transactions, address)
        
        # Combine all features
        enhanced = {**base_features, **velocity_features, **funding_features}
        
        # Add composite risk indicators
        enhanced['behavioral_risk_score'] = round(
            velocity_features['velocity_score'] * 0.4 +
            (1 - funding_features['funding_diversity_score']) * 0.3 +
            funding_features['circular_funding_flag'] * 0.3,
            3
        )
        
        return enhanced
    
    def prepare_training_data(self, df: pd.DataFrame) -> tuple:
        """
        Prepare features and labels for model training.
        
        Args:
            df: DataFrame with transaction data and 'is_malicious' column
        
        Returns:
            Tuple of (X features array, y labels array)
        """
        features_df = self.process_transaction_data(df)
        
        # Select feature columns (exclude target-related columns)
        feature_cols = [col for col in features_df.columns if col not in ['is_flash_loan']]
        X = features_df[feature_cols].values
        
        # Get labels
        if 'is_malicious' in df.columns:
            y = df['is_malicious'].astype(int).values
        else:
            y = np.zeros(len(df))
        
        return X, y, feature_cols


if __name__ == "__main__":
    # Test with sample data
    engineer = FeatureEngineer()
    print("Feature Engineer initialized.")
    
    # Load sample data
    try:
        sample_df = pd.read_csv("../../data/sample_transactions.csv")
        features = engineer.process_transaction_data(sample_df)
        print(f"Extracted {len(engineer.feature_names)} features:")
        print(engineer.feature_names)
    except FileNotFoundError:
        print("Sample data not found. Run from project root.")
