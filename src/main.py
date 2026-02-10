"""
Main Entry Point - Incident Predictor ML prediction loop.

This module provides the main entry point for the prediction engine,
orchestrating the detection cycle and integration with external systems.
"""

import asyncio
import time
from typing import Dict, List
from datetime import datetime
import os

from .prediction.anomaly_detector import AnomalyDetector
from .prediction.trajectory_predictor import TrajectoryPredictor
from .integration.sdf_bridge import SDFBridge
from .testing.mock_metrics import MockDynatraceAPI, MockMetricsGenerator


class IncidentPredictor:
    """
    Main prediction engine orchestrator.
    
    Runs the detection cycle:
    1. Fetch current metrics
    2. Detect anomalies using Z-score + Isolation Forest
    3. Predict trajectory and time-to-breach
    4. Filter by confidence threshold (>80%)
    5. Push high-confidence predictions to SDF
    """
    
    def __init__(
        self,
        anomaly_detector: AnomalyDetector,
        trajectory_predictor: TrajectoryPredictor,
        sdf_bridge: SDFBridge,
        metrics_api: MockDynatraceAPI,
        detection_interval_seconds: int = 60
    ):
        """
        Initialize the incident predictor.
        
        Args:
            anomaly_detector: AnomalyDetector instance
            trajectory_predictor: TrajectoryPredictor instance
            sdf_bridge: SDFBridge instance
            metrics_api: Metrics API client (real or mock)
            detection_interval_seconds: Seconds between detection cycles
        """
        self.anomaly_detector = anomaly_detector
        self.trajectory_predictor = trajectory_predictor
        self.sdf_bridge = sdf_bridge
        self.metrics_api = metrics_api
        self.detection_interval_seconds = detection_interval_seconds
        self.running = False
        
    async def run_detection_cycle(self) -> Dict:
        """
        Run a single detection cycle.
        
        Returns:
            Dictionary with cycle results and statistics
        """
        cycle_start = time.time()
        
        try:
            # 1. Fetch current metrics
            current_metrics = self.metrics_api.get_current_values()
            
            if not current_metrics:
                return {
                    "success": False,
                    "error": "No metrics available",
                    "duration_ms": 0
                }
            
            # 2. Fetch baseline data for each metric
            baseline_data = {}
            for metric_name in current_metrics.keys():
                baseline_values = self.metrics_api.get_baseline_values(metric_name)
                if baseline_values:
                    baseline_data[metric_name] = baseline_values
            
            # 3. Detect anomalies
            anomalies = self.anomaly_detector.detect_anomalies_batch(
                current_metrics,
                baseline_data,
                timestamp=datetime.now()
            )
            
            # 4. Generate predictions from anomalies
            predictions = self.trajectory_predictor.predict_from_anomalies(anomalies)
            
            # 5. Push high-confidence predictions to SDF
            push_results = {"success": 0, "failed": 0, "total": 0}
            if predictions:
                push_results = await self.sdf_bridge.push_predictions_batch(predictions)
            
            cycle_duration_ms = (time.time() - cycle_start) * 1000
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "metrics_checked": len(current_metrics),
                "anomalies_detected": len([a for a in anomalies if a.is_anomaly]),
                "predictions_generated": len(predictions),
                "high_confidence_predictions": len([p for p in predictions if p.confidence >= 80]),
                "sdf_push_results": push_results,
                "duration_ms": round(cycle_duration_ms, 2),
                "predictions": [p.to_dict() for p in predictions]
            }
            
        except Exception as e:
            cycle_duration_ms = (time.time() - cycle_start) * 1000
            return {
                "success": False,
                "error": str(e),
                "duration_ms": round(cycle_duration_ms, 2)
            }
    
    async def start(self) -> None:
        """
        Start the prediction loop.
        
        Runs continuously until stopped.
        """
        self.running = True
        print(f"[Incident Predictor] Starting prediction loop (interval: {self.detection_interval_seconds}s)")
        
        cycle_count = 0
        
        while self.running:
            cycle_count += 1
            print(f"\n[Incident Predictor] === Cycle {cycle_count} ===")
            
            result = await self.run_detection_cycle()
            
            if result["success"]:
                print(f"[Incident Predictor] Cycle completed in {result['duration_ms']}ms")
                print(f"  - Metrics checked: {result['metrics_checked']}")
                print(f"  - Anomalies detected: {result['anomalies_detected']}")
                print(f"  - Predictions generated: {result['predictions_generated']}")
                print(f"  - High-confidence predictions: {result['high_confidence_predictions']}")
                
                if result["predictions"]:
                    print(f"\n[Predictions]")
                    for pred in result["predictions"]:
                        print(f"  - {pred['prediction_type']}: {pred['explanation']}")
                        print(f"    Action: {pred['recommended_action']}")
            else:
                print(f"[Incident Predictor] Cycle failed: {result.get('error', 'Unknown error')}")
            
            # Wait before next cycle
            await asyncio.sleep(self.detection_interval_seconds)
    
    def stop(self) -> None:
        """
        Stop the prediction loop.
        """
        print("[Incident Predictor] Stopping prediction loop...")
        self.running = False


async def main():
    """
    Main entry point for the prediction engine.
    
    Configurable via environment variables:
    - DETECTION_INTERVAL_SECONDS: Time between detection cycles (default: 60)
    - SDF_ENDPOINT: SDF API endpoint URL
    - SDF_API_KEY: SDF API key for authentication
    - MOCK_MODE: Use mock data instead of real Dynatrace API (default: true)
    """
    # Configuration from environment
    detection_interval = int(os.getenv("DETECTION_INTERVAL_SECONDS", "60"))
    sdf_endpoint = os.getenv("SDF_ENDPOINT", "https://sdf-gold.internal/api/events")
    sdf_api_key = os.getenv("SDF_API_KEY")  # None = mock mode
    mock_mode = os.getenv("MOCK_MODE", "true").lower() == "true"
    
    print("[Incident Predictor ML] Initializing...")
    print(f"  - Detection interval: {detection_interval}s")
    print(f"  - Mock mode: {mock_mode}")
    print(f"  - SDF endpoint: {sdf_endpoint}")
    
    # Initialize components
    anomaly_detector = AnomalyDetector(baseline_window_hours=24)
    trajectory_predictor = TrajectoryPredictor(min_confidence=80.0)
    sdf_bridge = SDFBridge(sdf_endpoint=sdf_endpoint, api_key=sdf_api_key)
    
    # Initialize metrics API (mock or real)
    if mock_mode:
        print("[Incident Predictor ML] Using mock Dynatrace API")
        metrics_generator = MockMetricsGenerator()
        metrics_api = MockDynatraceAPI(metrics_generator)
        # Load CPU spike scenario for demo
        metrics_api.load_scenario("cpu_spike")
    else:
        # TODO: Initialize real Dynatrace API client
        raise NotImplementedError("Real Dynatrace API integration not yet implemented")
    
    # Create predictor
    predictor = IncidentPredictor(
        anomaly_detector=anomaly_detector,
        trajectory_predictor=trajectory_predictor,
        sdf_bridge=sdf_bridge,
        metrics_api=metrics_api,
        detection_interval_seconds=detection_interval
    )
    
    # Run prediction loop
    try:
        await predictor.start()
    except KeyboardInterrupt:
        print("\n[Incident Predictor ML] Received interrupt signal")
        predictor.stop()
    except Exception as e:
        print(f"[Incident Predictor ML] Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
