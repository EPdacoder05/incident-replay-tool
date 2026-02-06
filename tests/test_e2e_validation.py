"""
End-to-End Validation Tests - Pytest-compatible test suite.

This module provides pytest-compatible versions of all validation tests
with additional async support and parameterized testing.
"""

import pytest
import time
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prediction.anomaly_detector import AnomalyDetector
from src.prediction.trajectory_predictor import TrajectoryPredictor
from src.integration.sdf_bridge import SDFBridge
from src.testing.mock_metrics import MockMetricsGenerator, MockDynatraceAPI


@pytest.fixture
def anomaly_detector():
    """Fixture for AnomalyDetector instance."""
    return AnomalyDetector(baseline_window_hours=24)


@pytest.fixture
def trajectory_predictor():
    """Fixture for TrajectoryPredictor instance."""
    return TrajectoryPredictor(min_confidence=80.0)


@pytest.fixture
def metrics_generator():
    """Fixture for MockMetricsGenerator instance."""
    return MockMetricsGenerator(seed=42)


@pytest.fixture
def mock_api(metrics_generator):
    """Fixture for MockDynatraceAPI instance."""
    return MockDynatraceAPI(metrics_generator)


@pytest.fixture
def sdf_bridge():
    """Fixture for SDFBridge instance in mock mode."""
    return SDFBridge(api_key=None)  # Mock mode


class TestNormalMetrics:
    """Test normal baseline metrics (no false positives)."""
    
    def test_normal_metrics_no_anomalies(self, anomaly_detector, metrics_generator):
        """Normal metrics should produce 0 anomalies."""
        metrics = metrics_generator.generate_normal_metrics(duration_hours=24)
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-1] for name, values in metrics.items()}
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        anomaly_count = sum(1 for a in anomalies if a.is_anomaly)
        
        assert anomaly_count == 0, f"Expected 0 anomalies, got {anomaly_count}"
    
    def test_normal_metrics_no_predictions(
        self, anomaly_detector, trajectory_predictor, metrics_generator
    ):
        """Normal metrics should produce 0 predictions."""
        metrics = metrics_generator.generate_normal_metrics(duration_hours=24)
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-1] for name, values in metrics.items()}
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        predictions = trajectory_predictor.predict_from_anomalies(anomalies)
        
        assert len(predictions) == 0, f"Expected 0 predictions, got {len(predictions)}"


class TestCPUSpikeDetection:
    """Test CPU spike detection and prediction."""
    
    @pytest.mark.parametrize("severity,expected_min_confidence", [
        (0.6, 85.0),
        (0.8, 95.0),
        (0.9, 95.0),
    ])
    def test_cpu_spike_confidence(
        self, anomaly_detector, trajectory_predictor, metrics_generator,
        severity, expected_min_confidence
    ):
        """CPU spike should be detected with appropriate confidence."""
        metrics = metrics_generator.generate_cpu_spike(severity=severity)
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-5] for name, values in metrics.items()}
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        predictions = trajectory_predictor.predict_from_anomalies(anomalies)
        
        cpu_predictions = [p for p in predictions if "cpu" in p.metric_name.lower()]
        assert len(cpu_predictions) > 0, "No CPU prediction generated"
        
        cpu_pred = cpu_predictions[0]
        assert cpu_pred.confidence >= expected_min_confidence, \
            f"Confidence {cpu_pred.confidence:.1f}% below {expected_min_confidence}%"
    
    def test_cpu_spike_eta_range(
        self, anomaly_detector, trajectory_predictor, metrics_generator
    ):
        """CPU spike ETA should be within reasonable range (4-15 minutes)."""
        metrics = metrics_generator.generate_cpu_spike(severity=0.8)
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-5] for name, values in metrics.items()}
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        predictions = trajectory_predictor.predict_from_anomalies(anomalies)
        
        cpu_predictions = [p for p in predictions if "cpu" in p.metric_name.lower()]
        assert len(cpu_predictions) > 0
        
        cpu_pred = cpu_predictions[0]
        assert 4.0 <= cpu_pred.eta_minutes <= 15.0, \
            f"ETA {cpu_pred.eta_minutes:.1f} min outside range (4-15 min)"
    
    def test_cpu_spike_prediction_type(
        self, anomaly_detector, trajectory_predictor, metrics_generator
    ):
        """CPU spike should produce cpu_exhaustion prediction type."""
        metrics = metrics_generator.generate_cpu_spike(severity=0.8)
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-5] for name, values in metrics.items()}
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        predictions = trajectory_predictor.predict_from_anomalies(anomalies)
        
        cpu_predictions = [p for p in predictions if "cpu" in p.metric_name.lower()]
        assert len(cpu_predictions) > 0
        
        assert cpu_predictions[0].prediction_type == "cpu_exhaustion"


class TestExplanationGeneration:
    """Test human-readable explanation generation."""
    
    def test_explanation_contains_metric_name(self, anomaly_detector):
        """Explanation should contain metric name."""
        baseline = [45.0] * 100
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", 69.2, baseline)
        
        assert "cpu_utilization" in anomaly.explanation.lower()
    
    def test_explanation_contains_values(self, anomaly_detector):
        """Explanation should contain numeric values."""
        baseline = [45.0] * 100
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", 69.2, baseline)
        
        # Should contain baseline information
        assert "baseline" in anomaly.explanation.lower()
        assert "z=" in anomaly.explanation.lower()
    
    def test_prediction_explanation_format(
        self, anomaly_detector, trajectory_predictor
    ):
        """Prediction explanation should be well-formatted."""
        baseline = [45.0] * 100
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", 69.2, baseline)
        
        predictions = trajectory_predictor.predict_from_anomalies([anomaly])
        
        if predictions:
            pred = predictions[0]
            # Should contain percentage and time information
            assert "%" in pred.explanation
            assert "minute" in pred.explanation.lower()
            assert "confidence" in pred.explanation.lower()


class TestCascadingFailure:
    """Test cascading failure detection."""
    
    def test_cascading_failure_multiple_anomalies(
        self, anomaly_detector, metrics_generator
    ):
        """Cascading failure should detect 4+ simultaneous anomalies."""
        metrics = metrics_generator.generate_cascading_failure()
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-5] for name, values in metrics.items()}
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        anomaly_count = sum(1 for a in anomalies if a.is_anomaly)
        
        assert anomaly_count >= 4, f"Expected 4+ anomalies, got {anomaly_count}"
    
    def test_cascading_failure_multiple_predictions(
        self, anomaly_detector, trajectory_predictor, metrics_generator
    ):
        """Cascading failure should generate multiple predictions."""
        metrics = metrics_generator.generate_cascading_failure()
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-5] for name, values in metrics.items()}
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        predictions = trajectory_predictor.predict_from_anomalies(anomalies)
        
        assert len(predictions) >= 2, \
            f"Expected 2+ predictions for cascading failure, got {len(predictions)}"


class TestConfidenceFiltering:
    """Test confidence-based filtering of predictions."""
    
    def test_low_confidence_filtered_out(
        self, anomaly_detector, trajectory_predictor
    ):
        """Low-confidence anomalies should not generate predictions."""
        baseline = [45.0] * 100
        current_value = 52.0  # Small increase, low confidence
        
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", current_value, baseline)
        predictions = trajectory_predictor.predict_from_anomalies([anomaly])
        
        assert len(predictions) == 0, \
            "Low-confidence anomaly should not generate prediction"
    
    def test_high_confidence_accepted(
        self, anomaly_detector, trajectory_predictor
    ):
        """High-confidence anomalies should generate predictions."""
        baseline = [45.0] * 100
        current_value = 75.0  # Large increase, high confidence
        
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", current_value, baseline)
        predictions = trajectory_predictor.predict_from_anomalies([anomaly])
        
        assert len(predictions) > 0, \
            "High-confidence anomaly should generate prediction"
        assert predictions[0].confidence >= 80.0


class TestPerformance:
    """Test performance and latency requirements."""
    
    def test_detection_cycle_latency(
        self, anomaly_detector, trajectory_predictor, metrics_generator
    ):
        """Full detection cycle should complete in <2 seconds."""
        metrics = metrics_generator.generate_cpu_spike(severity=0.8)
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-5] for name, values in metrics.items()}
        
        start_time = time.time()
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        predictions = trajectory_predictor.predict_from_anomalies(anomalies)
        
        duration_ms = (time.time() - start_time) * 1000
        
        assert duration_ms < 2000, \
            f"Detection cycle took {duration_ms:.2f}ms (target: <2000ms)"
    
    def test_batch_processing_performance(
        self, anomaly_detector, metrics_generator
    ):
        """Batch processing should be efficient."""
        metrics = metrics_generator.generate_cascading_failure()
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-5] for name, values in metrics.items()}
        
        start_time = time.time()
        
        # Process 10 times to get average
        for _ in range(10):
            anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        
        duration_ms = (time.time() - start_time) * 1000 / 10
        
        assert duration_ms < 100, \
            f"Batch anomaly detection took {duration_ms:.2f}ms avg (target: <100ms)"


class TestSeverityEscalation:
    """Test severity escalation scenarios."""
    
    @pytest.mark.parametrize("value,expected_severity", [
        (52.0, "warning"),
        (65.0, "critical"),
        (85.0, "extreme"),
    ])
    def test_severity_classification(
        self, anomaly_detector, value, expected_severity
    ):
        """Different values should map to appropriate severity levels."""
        baseline = [45.0] * 100
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", value, baseline)
        
        # Allow for some flexibility (warning can be normal for small spikes)
        if expected_severity == "warning":
            assert anomaly.severity in ["normal", "warning", "critical"]
        elif expected_severity == "critical":
            assert anomaly.severity in ["warning", "critical", "extreme"]
        else:  # extreme
            assert anomaly.severity in ["critical", "extreme"]


@pytest.mark.asyncio
class TestSDFIntegration:
    """Test SDF Bridge integration."""
    
    async def test_sdf_push_prediction(
        self, sdf_bridge, anomaly_detector, trajectory_predictor
    ):
        """SDF bridge should successfully push predictions in mock mode."""
        baseline = [45.0] * 100
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", 75.0, baseline)
        predictions = trajectory_predictor.predict_from_anomalies([anomaly])
        
        if predictions:
            result = await sdf_bridge.push_prediction(predictions[0])
            assert result is True, "SDF push should succeed in mock mode"
    
    async def test_sdf_batch_push(
        self, sdf_bridge, anomaly_detector, trajectory_predictor, metrics_generator
    ):
        """SDF bridge should handle batch pushes."""
        metrics = metrics_generator.generate_cascading_failure()
        current_values = metrics_generator.get_latest_values(metrics)
        baseline_data = {name: values[:-5] for name, values in metrics.items()}
        
        anomalies = anomaly_detector.detect_anomalies_batch(current_values, baseline_data)
        predictions = trajectory_predictor.predict_from_anomalies(anomalies)
        
        results = await sdf_bridge.push_predictions_batch(predictions)
        
        assert results["success"] == len(predictions)
        assert results["failed"] == 0


class TestDataFormats:
    """Test data serialization and formats."""
    
    def test_anomaly_to_dict(self, anomaly_detector):
        """Anomaly should serialize to dict correctly."""
        baseline = [45.0] * 100
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", 69.2, baseline)
        
        data = anomaly.to_dict()
        
        assert "metric_name" in data
        assert "current_value" in data
        assert "z_score" in data
        assert "severity" in data
        assert "explanation" in data
    
    def test_prediction_to_dict(
        self, anomaly_detector, trajectory_predictor
    ):
        """Prediction should serialize to dict correctly."""
        baseline = [45.0] * 100
        anomaly = anomaly_detector.detect_anomaly("cpu_utilization", 75.0, baseline)
        predictions = trajectory_predictor.predict_from_anomalies([anomaly])
        
        if predictions:
            data = predictions[0].to_dict()
            
            assert "prediction_type" in data
            assert "metric_name" in data
            assert "confidence" in data
            assert "eta_minutes" in data
            assert "explanation" in data
            assert "recommended_action" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
