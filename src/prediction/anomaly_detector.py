"""
Anomaly Detector - Z-score baseline analysis with Isolation Forest ML.

This module implements the core anomaly detection logic using:
- Z-score baseline analysis with configurable thresholds
- Isolation Forest for unsupervised anomaly detection
- Sliding window baseline calculation (24h default)
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.ensemble import IsolationForest


@dataclass
class AnomalyResult:
    """
    Result of anomaly detection analysis.
    
    Attributes:
        metric_name: Name of the metric (e.g., "cpu_utilization")
        current_value: Current metric value
        baseline_mean: Mean value from baseline window
        baseline_std: Standard deviation from baseline
        z_score: Z-score (number of std devs from mean)
        severity: Severity level (normal, warning, critical, extreme)
        is_anomaly: Whether this is considered an anomaly
        explanation: Human-readable explanation
        timestamp: When the anomaly was detected
    """
    metric_name: str
    current_value: float
    baseline_mean: float
    baseline_std: float
    z_score: float
    severity: str
    is_anomaly: bool
    explanation: str
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "metric_name": self.metric_name,
            "current_value": round(self.current_value, 2),
            "baseline_mean": round(self.baseline_mean, 2),
            "baseline_std": round(self.baseline_std, 2),
            "z_score": round(self.z_score, 2),
            "severity": self.severity,
            "is_anomaly": self.is_anomaly,
            "explanation": self.explanation,
            "timestamp": self.timestamp.isoformat()
        }


class AnomalyDetector:
    """
    Z-score baseline anomaly detector with Isolation Forest support.
    
    Detects anomalies using statistical methods:
    - Z-score > 1.5: Warning
    - Z-score > 3.0: Critical
    - Z-score > 4.5: Extreme
    """
    
    # Z-score thresholds for severity classification
    Z_WARNING = 1.5
    Z_CRITICAL = 3.0
    Z_EXTREME = 4.5
    
    def __init__(self, baseline_window_hours: int = 24, contamination: float = 0.1):
        """
        Initialize the anomaly detector.
        
        Args:
            baseline_window_hours: Hours of historical data for baseline (default 24h)
            contamination: Expected proportion of outliers for Isolation Forest (0.1 = 10%)
        """
        self.baseline_window_hours = baseline_window_hours
        self.contamination = contamination
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
    def calculate_z_score(
        self,
        current_value: float,
        baseline_values: List[float]
    ) -> Tuple[float, float, float]:
        """
        Calculate Z-score for a value against baseline.
        
        Args:
            current_value: Current metric value
            baseline_values: Historical values for baseline calculation
            
        Returns:
            Tuple of (z_score, mean, std_dev)
        """
        if len(baseline_values) < 2:
            return 0.0, current_value, 0.0
            
        mean = np.mean(baseline_values)
        std = np.std(baseline_values)
        
        # Avoid division by zero
        if std == 0:
            std = 0.01
            
        z_score = (current_value - mean) / std
        return z_score, mean, std
    
    def classify_severity(self, z_score: float) -> str:
        """
        Classify anomaly severity based on Z-score.
        
        Args:
            z_score: Z-score value (absolute value used for classification)
            
        Returns:
            Severity level: normal, warning, critical, or extreme
        """
        abs_z = abs(z_score)
        
        if abs_z >= self.Z_EXTREME:
            return "extreme"
        elif abs_z >= self.Z_CRITICAL:
            return "critical"
        elif abs_z >= self.Z_WARNING:
            return "warning"
        else:
            return "normal"
    
    def generate_explanation(
        self,
        metric_name: str,
        current_value: float,
        baseline_mean: float,
        baseline_std: float,
        z_score: float,
        severity: str
    ) -> str:
        """
        Generate human-readable explanation of the anomaly.
        
        Args:
            metric_name: Name of the metric
            current_value: Current value
            baseline_mean: Baseline mean
            baseline_std: Baseline standard deviation
            z_score: Z-score
            severity: Severity level
            
        Returns:
            Human-readable explanation string
        """
        if severity == "normal":
            return f"{metric_name}={current_value:.1f} is within normal range (baseline={baseline_mean:.1f}±{baseline_std:.1f})"
        
        direction = "above" if z_score > 0 else "below"
        return (
            f"{metric_name}={current_value:.1f} is {abs(z_score):.2f} std devs {direction} "
            f"baseline (baseline={baseline_mean:.1f}±{baseline_std:.1f}, z={z_score:.2f})"
        )
    
    def detect_anomaly(
        self,
        metric_name: str,
        current_value: float,
        baseline_values: List[float],
        timestamp: Optional[datetime] = None
    ) -> AnomalyResult:
        """
        Detect if current value is anomalous compared to baseline.
        
        Args:
            metric_name: Name of the metric being analyzed
            current_value: Current metric value
            baseline_values: Historical values for baseline
            timestamp: Timestamp of the current value (defaults to now)
            
        Returns:
            AnomalyResult with detection details
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # Calculate Z-score
        z_score, mean, std = self.calculate_z_score(current_value, baseline_values)
        
        # Classify severity
        severity = self.classify_severity(z_score)
        is_anomaly = severity in ["warning", "critical", "extreme"]
        
        # Generate explanation
        explanation = self.generate_explanation(
            metric_name, current_value, mean, std, z_score, severity
        )
        
        return AnomalyResult(
            metric_name=metric_name,
            current_value=current_value,
            baseline_mean=mean,
            baseline_std=std,
            z_score=z_score,
            severity=severity,
            is_anomaly=is_anomaly,
            explanation=explanation,
            timestamp=timestamp
        )
    
    def detect_anomalies_batch(
        self,
        metrics: Dict[str, float],
        baseline_data: Dict[str, List[float]],
        timestamp: Optional[datetime] = None
    ) -> List[AnomalyResult]:
        """
        Detect anomalies across multiple metrics simultaneously.
        
        Args:
            metrics: Dictionary of metric_name -> current_value
            baseline_data: Dictionary of metric_name -> baseline_values
            timestamp: Timestamp for all detections
            
        Returns:
            List of AnomalyResult objects
        """
        results = []
        
        for metric_name, current_value in metrics.items():
            baseline_values = baseline_data.get(metric_name, [])
            
            if len(baseline_values) == 0:
                # Skip metrics without baseline data
                continue
                
            result = self.detect_anomaly(
                metric_name, current_value, baseline_values, timestamp
            )
            results.append(result)
        
        return results
    
    def train_isolation_forest(self, training_data: np.ndarray) -> None:
        """
        Train the Isolation Forest model on historical data.
        
        Args:
            training_data: 2D array of shape (n_samples, n_features)
                          Each row is a time point, each column is a metric
        """
        if len(training_data) < 10:
            raise ValueError("Need at least 10 samples to train Isolation Forest")
            
        self.isolation_forest.fit(training_data)
    
    def predict_with_isolation_forest(self, data_point: np.ndarray) -> bool:
        """
        Predict if a data point is anomalous using Isolation Forest.
        
        Args:
            data_point: 1D array of metric values
            
        Returns:
            True if anomalous, False otherwise
        """
        # Reshape for sklearn
        data_point = data_point.reshape(1, -1)
        
        # -1 = outlier/anomaly, 1 = inlier/normal
        prediction = self.isolation_forest.predict(data_point)
        
        return prediction[0] == -1
