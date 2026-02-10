"""
Trajectory Predictor - Linear trajectory extrapolation and confidence scoring.

This module predicts when metrics will breach critical thresholds using:
- Linear trajectory extrapolation from anomaly trends
- Time-to-breach calculation
- Confidence scoring based on Z-score magnitude and trend consistency
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .anomaly_detector import AnomalyResult


@dataclass
class Prediction:
    """
    Prediction of future incident based on current trajectory.
    
    Attributes:
        prediction_type: Type of predicted incident (cpu_exhaustion, memory_exhaustion, etc.)
        metric_name: The metric being predicted
        current_value: Current metric value
        predicted_breach_value: Value at which incident occurs (e.g., 100%)
        eta_minutes: Estimated time to breach in minutes
        confidence: Confidence score (0-100%)
        growth_rate_per_minute: Rate of change per minute
        explanation: Human-readable prediction explanation
        recommended_action: Suggested remediation
        timestamp: When prediction was made
        anomaly_result: The underlying anomaly detection result
    """
    prediction_type: str
    metric_name: str
    current_value: float
    predicted_breach_value: float
    eta_minutes: float
    confidence: float
    growth_rate_per_minute: float
    explanation: str
    recommended_action: str
    timestamp: datetime
    anomaly_result: Optional[AnomalyResult] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        result = {
            "prediction_type": self.prediction_type,
            "metric_name": self.metric_name,
            "current_value": round(self.current_value, 2),
            "predicted_breach_value": round(self.predicted_breach_value, 2),
            "eta_minutes": round(self.eta_minutes, 2),
            "confidence": round(self.confidence, 2),
            "growth_rate_per_minute": round(self.growth_rate_per_minute, 4),
            "explanation": self.explanation,
            "recommended_action": self.recommended_action,
            "timestamp": self.timestamp.isoformat()
        }
        
        if self.anomaly_result:
            result["anomaly_details"] = self.anomaly_result.to_dict()
            
        return result


class TrajectoryPredictor:
    """
    Predicts future incidents by analyzing metric trajectories.
    
    Uses linear extrapolation and confidence scoring to predict:
    - CPU exhaustion
    - Memory exhaustion
    - Disk full
    - Network saturation
    """
    
    # Breach thresholds for different metric types
    BREACH_THRESHOLDS = {
        "cpu_utilization": 95.0,
        "memory_utilization": 95.0,
        "disk_utilization": 95.0,
        "network_utilization": 95.0,
        "error_rate": 10.0,  # 10% error rate
        "response_time_ms": 5000.0,  # 5 second response time
    }
    
    # Prediction types and their recommended actions
    PREDICTION_ACTIONS = {
        "cpu_exhaustion": "Scale out horizontally or increase instance size",
        "memory_exhaustion": "Investigate memory leaks, restart services, or scale up",
        "disk_full": "Clean up logs, expand storage, or enable auto-archiving",
        "network_saturation": "Check for DDoS, optimize queries, or increase bandwidth",
        "error_spike": "Check recent deployments, review logs, possible rollback",
        "latency_spike": "Check database performance, downstream dependencies",
    }
    
    def __init__(self, min_confidence: float = 80.0, max_prediction_window_minutes: int = 30):
        """
        Initialize the trajectory predictor.
        
        Args:
            min_confidence: Minimum confidence threshold for surfacing predictions (default 80%)
            max_prediction_window_minutes: Maximum time window for predictions (default 30 min)
        """
        self.min_confidence = min_confidence
        self.max_prediction_window_minutes = max_prediction_window_minutes
    
    def calculate_growth_rate(
        self,
        current_value: float,
        baseline_mean: float,
        time_window_minutes: float = 10.0
    ) -> float:
        """
        Calculate growth rate per minute based on current deviation from baseline.
        
        Args:
            current_value: Current metric value
            baseline_mean: Baseline mean value
            time_window_minutes: Time window for rate calculation
            
        Returns:
            Growth rate per minute
        """
        delta = current_value - baseline_mean
        
        if time_window_minutes <= 0:
            time_window_minutes = 10.0
            
        return delta / time_window_minutes
    
    def calculate_confidence(
        self,
        z_score: float,
        growth_rate: float,
        current_value: float,
        breach_threshold: float
    ) -> float:
        """
        Calculate confidence score for prediction.
        
        Confidence is based on:
        - Z-score magnitude (higher = more confident)
        - Growth rate consistency
        - Distance to breach threshold
        
        Args:
            z_score: Z-score from anomaly detection
            growth_rate: Rate of change per minute
            current_value: Current metric value
            breach_threshold: Threshold value for breach
            
        Returns:
            Confidence score (0-100%)
        """
        # Base confidence from Z-score magnitude
        # Z=1.5 -> 60%, Z=3.0 -> 80%, Z=4.5+ -> 95%
        abs_z = abs(z_score)
        if abs_z < 1.5:
            z_confidence = abs_z / 1.5 * 60.0
        elif abs_z < 3.0:
            z_confidence = 60.0 + (abs_z - 1.5) / 1.5 * 20.0
        else:
            z_confidence = 80.0 + min((abs_z - 3.0) / 1.5 * 15.0, 15.0)
        
        # Growth rate factor (positive growth increases confidence)
        if growth_rate > 0:
            growth_factor = 1.1  # 10% boost for positive growth
        else:
            growth_factor = 0.8  # 20% penalty for negative growth
        
        # Distance to threshold factor
        distance_ratio = (breach_threshold - current_value) / breach_threshold
        if distance_ratio < 0.1:
            distance_factor = 1.2  # Very close to breach
        elif distance_ratio < 0.3:
            distance_factor = 1.1  # Moderately close
        else:
            distance_factor = 1.0
        
        confidence = min(z_confidence * growth_factor * distance_factor, 99.9)
        return max(confidence, 0.0)
    
    def predict_time_to_breach(
        self,
        current_value: float,
        growth_rate: float,
        breach_threshold: float
    ) -> float:
        """
        Calculate estimated time to breach threshold.
        
        Args:
            current_value: Current metric value
            growth_rate: Rate of change per minute
            breach_threshold: Threshold value
            
        Returns:
            Estimated minutes to breach (or float('inf') if no breach predicted)
        """
        if growth_rate <= 0:
            return float('inf')  # Not growing, won't breach
        
        if current_value >= breach_threshold:
            return 0.0  # Already breached
        
        delta = breach_threshold - current_value
        eta_minutes = delta / growth_rate
        
        return eta_minutes
    
    def determine_prediction_type(self, metric_name: str) -> str:
        """
        Determine the type of prediction based on metric name.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Prediction type identifier
        """
        metric_lower = metric_name.lower()
        
        if "cpu" in metric_lower:
            return "cpu_exhaustion"
        elif "memory" in metric_lower or "mem" in metric_lower:
            return "memory_exhaustion"
        elif "disk" in metric_lower:
            return "disk_full"
        elif "network" in metric_lower:
            return "network_saturation"
        elif "error" in metric_lower:
            return "error_spike"
        elif "latency" in metric_lower or "response" in metric_lower:
            return "latency_spike"
        else:
            return "resource_exhaustion"
    
    def generate_explanation(
        self,
        metric_name: str,
        current_value: float,
        breach_threshold: float,
        eta_minutes: float,
        growth_rate: float,
        confidence: float
    ) -> str:
        """
        Generate human-readable prediction explanation.
        
        Args:
            metric_name: Name of the metric
            current_value: Current value
            breach_threshold: Breach threshold
            eta_minutes: Time to breach in minutes
            growth_rate: Growth rate per minute
            confidence: Confidence score
            
        Returns:
            Human-readable explanation
        """
        growth_pct = (growth_rate / current_value * 100) if current_value > 0 else 0
        
        return (
            f"{metric_name} at {current_value:.1f}% (growing {growth_pct:.2f}%/min) "
            f"will reach {breach_threshold:.0f}% in {eta_minutes:.1f} minutes "
            f"(confidence: {confidence:.0f}%)"
        )
    
    def predict_from_anomaly(
        self,
        anomaly: AnomalyResult,
        time_window_minutes: float = 10.0
    ) -> Optional[Prediction]:
        """
        Generate prediction from an anomaly detection result.
        
        Args:
            anomaly: AnomalyResult from anomaly detector
            time_window_minutes: Time window for growth rate calculation
            
        Returns:
            Prediction object if confidence is above threshold, None otherwise
        """
        # Only predict for anomalies with warning+ severity
        if anomaly.severity == "normal":
            return None
        
        # Determine breach threshold for this metric
        metric_type = anomaly.metric_name.lower()
        breach_threshold = None
        
        for key, value in self.BREACH_THRESHOLDS.items():
            if key.replace("_", "") in metric_type.replace("_", ""):
                breach_threshold = value
                break
        
        if breach_threshold is None:
            # Default to 100 for percentage metrics
            breach_threshold = 100.0
        
        # Calculate growth rate
        growth_rate = self.calculate_growth_rate(
            anomaly.current_value,
            anomaly.baseline_mean,
            time_window_minutes
        )
        
        # Calculate time to breach
        eta_minutes = self.predict_time_to_breach(
            anomaly.current_value,
            growth_rate,
            breach_threshold
        )
        
        # Skip if no breach predicted or beyond prediction window
        if eta_minutes == float('inf') or eta_minutes > self.max_prediction_window_minutes:
            return None
        
        # Calculate confidence
        confidence = self.calculate_confidence(
            anomaly.z_score,
            growth_rate,
            anomaly.current_value,
            breach_threshold
        )
        
        # Filter by minimum confidence
        if confidence < self.min_confidence:
            return None
        
        # Determine prediction type and recommended action
        prediction_type = self.determine_prediction_type(anomaly.metric_name)
        recommended_action = self.PREDICTION_ACTIONS.get(
            prediction_type,
            "Investigate immediately and scale resources if needed"
        )
        
        # Generate explanation
        explanation = self.generate_explanation(
            anomaly.metric_name,
            anomaly.current_value,
            breach_threshold,
            eta_minutes,
            growth_rate,
            confidence
        )
        
        return Prediction(
            prediction_type=prediction_type,
            metric_name=anomaly.metric_name,
            current_value=anomaly.current_value,
            predicted_breach_value=breach_threshold,
            eta_minutes=eta_minutes,
            confidence=confidence,
            growth_rate_per_minute=growth_rate,
            explanation=explanation,
            recommended_action=recommended_action,
            timestamp=anomaly.timestamp,
            anomaly_result=anomaly
        )
    
    def predict_from_anomalies(
        self,
        anomalies: List[AnomalyResult],
        time_window_minutes: float = 10.0
    ) -> List[Prediction]:
        """
        Generate predictions from multiple anomaly results.
        
        Args:
            anomalies: List of AnomalyResult objects
            time_window_minutes: Time window for growth rate calculation
            
        Returns:
            List of Prediction objects (only high-confidence predictions)
        """
        predictions = []
        
        for anomaly in anomalies:
            prediction = self.predict_from_anomaly(anomaly, time_window_minutes)
            if prediction:
                predictions.append(prediction)
        
        # Sort by ETA (most urgent first)
        predictions.sort(key=lambda p: p.eta_minutes)
        
        return predictions
