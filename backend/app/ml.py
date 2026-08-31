"""
ML layer for RevPilot.
Isolation Forest for anomaly detection.
Logistic Regression for recovery probability.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
import joblib
import os

# Model paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models_cache")
ANOMALY_MODEL_PATH = os.path.join(MODEL_DIR, "isolation_forest.pkl")
RECOVERY_MODEL_PATH = os.path.join(MODEL_DIR, "recovery_lr.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

# Create model directory
os.makedirs(MODEL_DIR, exist_ok=True)


class MLEngine:
    """Machine learning models for anomaly detection and recovery prediction"""
    
    @staticmethod
    def train_anomaly_detector(features_list: List[np.ndarray], contamination: float = 0.05) -> IsolationForest:
        """
        Train Isolation Forest for anomaly detection.
        features: (n_samples, n_features) array
        contamination: expected proportion of outliers
        """
        X = np.array(features_list)
        
        model = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
        model.fit(X)
        
        # Save model
        joblib.dump(model, ANOMALY_MODEL_PATH)
        return model
    
    @staticmethod
    def detect_anomaly(features: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if a transaction is anomalous.
        features: (n_features,) array
        Returns: (is_anomaly, anomaly_score)
        """
        # Load or train model if not exists
        if os.path.exists(ANOMALY_MODEL_PATH):
            model = joblib.load(ANOMALY_MODEL_PATH)
        else:
            # Return neutral if no model
            return False, 0.0
        
        prediction = model.predict([features])[0]
        score = model.score_samples([features])[0]
        
        # prediction: 1 = normal, -1 = anomaly
        is_anomaly = prediction == -1
        anomaly_score = -score  # Convert to 0-1 scale (higher = more anomalous)
        
        return is_anomaly, float(max(0, min(1, anomaly_score)))
    
    @staticmethod
    def train_recovery_model(X: np.ndarray, y: np.ndarray) -> Tuple[LogisticRegression, StandardScaler]:
        """
        Train Logistic Regression for recovery probability.
        X: (n_samples, n_features) - features
        y: (n_samples,) - binary labels (1 = recovered, 0 = not recovered)
        """
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_scaled, y)
        
        # Save models
        joblib.dump(model, RECOVERY_MODEL_PATH)
        joblib.dump(scaler, SCALER_PATH)
        
        return model, scaler
    
    @staticmethod
    def predict_recovery_probability(features: np.ndarray) -> float:
        """
        Predict probability of successful recovery for a transaction.
        features: (n_features,) array with [amount, customer_ltv, prior_success_rate, recency_days, payment_method_encoded]
        Returns: probability (0-1)
        """
        # Load or use default if model doesn't exist
        if not os.path.exists(RECOVERY_MODEL_PATH) or not os.path.exists(SCALER_PATH):
            # Simple heuristic if no model
            # Higher amounts, higher LTV, more recent = higher probability
            amount, ltv, success_rate, recency, method = features[:5]
            prob = (amount / 100000) * 0.3 + (ltv / 50000) * 0.3 + success_rate * 0.2 + (1 / (recency + 1)) * 0.2
            return float(max(0, min(1, prob)))
        
        model = joblib.load(RECOVERY_MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        
        X_scaled = scaler.transform([features])
        prob = model.predict_proba(X_scaled)[0][1]
        
        return float(prob)
    
    @staticmethod
    def feature_engineering_for_anomaly(transaction_dict: Dict) -> np.ndarray:
        """
        Engineer features for anomaly detection.
        Returns: (amount, frequency_in_window, success_rate, time_of_day, payment_method_encoded)
        """
        amount = transaction_dict.get('amount', 0.0)
        payment_method = transaction_dict.get('payment_method', 'unknown')
        hour_of_day = transaction_dict.get('hour', 12)
        
        # Encode payment method
        method_map = {'card': 1, 'upi': 2, 'netbanking': 3, 'wallet': 4, 'unknown': 0}
        method_encoded = method_map.get(payment_method, 0)
        
        # Normalize features
        amount_norm = min(1.0, amount / 100000)  # Normalize to max 100k
        hour_norm = hour_of_day / 24.0
        
        return np.array([amount_norm, method_encoded / 4.0, hour_norm])
    
    @staticmethod
    def feature_engineering_for_recovery(transaction_dict: Dict, customer_dict: Dict) -> np.ndarray:
        """
        Engineer features for recovery prediction.
        Returns: (amount, customer_ltv, prior_success_rate, recency_days, payment_method_encoded, failure_reason_encoded)
        """
        amount = transaction_dict.get('amount', 0.0)
        payment_method = transaction_dict.get('payment_method', 'unknown')
        failure_reason = transaction_dict.get('failure_reason', 'unknown')
        days_since_created = transaction_dict.get('days_since_created', 30)
        
        ltv = customer_dict.get('lifetime_value', 0.0)
        prior_success_rate = customer_dict.get('success_rate', 0.5)
        
        # Encode payment method
        method_map = {'card': 1, 'upi': 2, 'netbanking': 3, 'wallet': 4, 'unknown': 0}
        method_encoded = method_map.get(payment_method, 0)
        
        # Encode failure reason
        reason_map = {
            'insufficient_funds': 1,
            'card_declined': 2,
            'invalid_cvv': 3,
            'timeout': 0,  # Lower recovery for timeout
            'network_error': 0,
            '3ds_failed': 2,
            'unknown': 0.5
        }
        reason_encoded = reason_map.get(failure_reason, 0.5)
        
        # Normalize features
        amount_norm = min(1.0, amount / 100000)
        ltv_norm = min(1.0, ltv / 50000)
        recency_norm = 1.0 / (days_since_created + 1)
        
        return np.array([amount_norm, ltv_norm, prior_success_rate, recency_norm, method_encoded / 4.0, reason_encoded / 3.0])


class TrainingData:
    """Helper for generating training data from synthetic dataset"""
    
    @staticmethod
    def prepare_anomaly_training_data(transactions: List[Dict]) -> np.ndarray:
        """Convert transaction list to feature matrix for anomaly detection"""
        features = []
        for tx in transactions:
            feat = MLEngine.feature_engineering_for_anomaly(tx)
            features.append(feat)
        return np.array(features)
    
    @staticmethod
    def prepare_recovery_training_data(failed_transactions: List[Dict], customers: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for recovery model"""
        X = []
        y = []  # Binary: 1 if recovered, 0 if not
        
        for tx in failed_transactions:
            customer_id = tx.get('customer_id')
            customer = customers.get(customer_id, {})
            
            feat = MLEngine.feature_engineering_for_recovery(tx, customer)
            X.append(feat)
            
            # For synthetic data: assume higher LTV + higher success rate = likely recovered
            customer_ltv = customer.get('lifetime_value', 0.0)
            success_rate = customer.get('success_rate', 0.0)
            recovered = 1 if (customer_ltv > 10000 and success_rate > 0.8) else 0
            y.append(recovered)
        
        return np.array(X), np.array(y)


def initialize_ml_models():
    """
    Initialize ML models from synthetic data.
    Called on first startup or can be called manually for retraining.
    """
    # This will be called from the agent during initialization
    pass
