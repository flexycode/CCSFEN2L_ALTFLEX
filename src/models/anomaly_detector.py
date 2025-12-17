"""
Anomaly Detector Module.

This module implements tabular anomaly detection using XGBoost for identifying
suspicious blockchain transactions and potential flash loan attacks.
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier = None
    print("Warning: XGBoost not installed. Install with: pip install xgboost")

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


class AnomalyDetector:
    """
    XGBoost-based anomaly detector for blockchain transaction analysis.
    Designed to detect flash loan attacks and suspicious activity patterns.
    """
    
    DEFAULT_PARAMS = {
        'n_estimators': 100,
        'max_depth': 6,
        'learning_rate': 0.1,
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'use_label_encoder': False,
        'random_state': 42
    }
    
    def __init__(self, model_path: Optional[str] = None, params: Optional[Dict] = None):
        """
        Initialize the anomaly detector.
        
        Args:
            model_path: Path to a pre-trained model file
            params: Custom XGBoost parameters (optional)
        """
        self.model_path = model_path
        self.params = params or self.DEFAULT_PARAMS
        self.model = None
        self.feature_names: List[str] = []
        self.is_trained = False
        self.training_stats: Dict[str, Any] = {}
        
        if XGBClassifier is None:
            raise ImportError("XGBoost is required. Install with: pip install xgboost")
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.model = XGBClassifier(**self.params)
    
    def train(self, X: np.ndarray, y: np.ndarray, 
              feature_names: Optional[List[str]] = None,
              validation_split: float = 0.2) -> Dict[str, Any]:
        """
        Train the XGBoost model on labeled data.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Binary labels (0 = normal, 1 = malicious)
            feature_names: Names of features for interpretability
            validation_split: Fraction of data for validation
        
        Returns:
            Dictionary with training metrics
        """
        print(f"Training anomaly detector on {len(X)} samples...")
        
        self.feature_names = feature_names or [f"feature_{i}" for i in range(X.shape[1])]
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=42, stratify=y if len(np.unique(y)) > 1 else None
        )
        
        # Train model
        self.model = XGBClassifier(**self.params)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        # Calculate metrics
        y_pred = self.model.predict(X_val)
        y_prob = self.model.predict_proba(X_val)[:, 1]
        
        self.training_stats = {
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'val_accuracy': (y_pred == y_val).mean(),
            'val_roc_auc': roc_auc_score(y_val, y_prob) if len(np.unique(y_val)) > 1 else 0.0,
            'feature_importance': self.get_feature_importance(),
            'trained_at': datetime.now().isoformat()
        }
        
        self.is_trained = True
        print(f"Training complete. Validation accuracy: {self.training_stats['val_accuracy']:.4f}")
        
        return self.training_stats
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict labels for new data.
        
        Args:
            X: Feature matrix (n_samples, n_features)
        
        Returns:
            Binary predictions (0 = normal, 1 = malicious)
        """
        if not self.is_trained and self.model is None:
            raise ValueError("Model not trained. Call train() first or load a pre-trained model.")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get probability scores for predictions.
        
        Args:
            X: Feature matrix (n_samples, n_features)
        
        Returns:
            Probability scores for each class
        """
        if not self.is_trained and self.model is None:
            raise ValueError("Model not trained. Call train() first or load a pre-trained model.")
        
        return self.model.predict_proba(X)
    
    def detect(self, X: np.ndarray, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Run full detection pipeline with confidence scores.
        
        Args:
            X: Feature matrix
            threshold: Probability threshold for flagging as malicious
        
        Returns:
            List of detection results with confidence scores
        """
        probabilities = self.predict_proba(X)
        predictions = (probabilities[:, 1] >= threshold).astype(int)
        
        results = []
        for i in range(len(X)):
            results.append({
                'index': i,
                'is_malicious': bool(predictions[i]),
                'confidence': float(probabilities[i, 1]),
                'risk_level': self._get_risk_level(probabilities[i, 1])
            })
        
        return results
    
    def _get_risk_level(self, prob: float) -> str:
        """Convert probability to human-readable risk level."""
        if prob >= 0.9:
            return "CRITICAL"
        elif prob >= 0.7:
            return "HIGH"
        elif prob >= 0.5:
            return "MEDIUM"
        elif prob >= 0.3:
            return "LOW"
        else:
            return "MINIMAL"
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None:
            return {}
        
        try:
            importances = self.model.feature_importances_
            return dict(zip(self.feature_names, importances.tolist()))
        except Exception:
            return {}
    
    def save_model(self, path: str) -> None:
        """
        Save the trained model to disk.
        
        Args:
            path: File path to save the model
        """
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")
        
        # Create directory if needed
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'training_stats': self.training_stats,
            'params': self.params
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {path}")
    
    def load_model(self, path: str) -> None:
        """
        Load a pre-trained model from disk.
        
        Args:
            path: File path to the saved model
        """
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.feature_names = model_data.get('feature_names', [])
        self.training_stats = model_data.get('training_stats', {})
        self.params = model_data.get('params', self.DEFAULT_PARAMS)
        self.is_trained = True
        
        print(f"Model loaded from {path}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model state."""
        return {
            'is_trained': self.is_trained,
            'model_type': 'XGBClassifier',
            'n_features': len(self.feature_names),
            'feature_names': self.feature_names,
            'training_stats': self.training_stats,
            'params': self.params
        }


def train_from_csv(csv_path: str, model_save_path: str = "models/anomaly_detector.pkl") -> AnomalyDetector:
    """
    Utility function to train a detector from a CSV file.
    
    Args:
        csv_path: Path to CSV with transaction data
        model_save_path: Where to save the trained model
    
    Returns:
        Trained AnomalyDetector instance
    """
    from .feature_engineer import FeatureEngineer
    
    # Load data
    df = pd.read_csv(csv_path)
    
    # Extract features
    engineer = FeatureEngineer()
    X, y, feature_names = engineer.prepare_training_data(df)
    
    # Train model
    detector = AnomalyDetector()
    detector.train(X, y, feature_names)
    
    # Save model
    detector.save_model(model_save_path)
    
    return detector


if __name__ == "__main__":
    # Demo - create and test the detector
    detector = AnomalyDetector()
    print("Anomaly Detector initialized.")
    print(f"Model info: {detector.get_model_info()}")
