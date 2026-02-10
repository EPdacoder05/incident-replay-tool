"""
Security Data Fabric (SDF) Bridge - Integration with Gold layer.

This module provides a bridge to push predictions to the Security Data Fabric
Gold layer as enriched security events.
"""

import httpx
import json
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from ..prediction.trajectory_predictor import Prediction


class SDFBridge:
    """
    Bridge to Security Data Fabric Gold layer.
    
    Pushes predictions as enriched security events with retry logic.
    """
    
    def __init__(
        self,
        sdf_endpoint: str = "https://sdf-gold.internal/api/events",
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: int = 10
    ):
        """
        Initialize SDF Bridge.
        
        Args:
            sdf_endpoint: SDF API endpoint URL
            api_key: API key for authentication (if None, uses mock mode)
            max_retries: Maximum number of retry attempts
            timeout_seconds: Request timeout in seconds
        """
        self.sdf_endpoint = sdf_endpoint
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.mock_mode = api_key is None
        
    def format_prediction_event(self, prediction: Prediction) -> Dict:
        """
        Format a prediction as an SDF event.
        
        Args:
            prediction: Prediction object to format
            
        Returns:
            Dictionary formatted for SDF API
        """
        event = {
            "event_type": "predictive_incident_alert",
            "timestamp": prediction.timestamp.isoformat(),
            "severity": self._map_confidence_to_severity(prediction.confidence),
            "source": "incident-predictor-ml",
            "prediction": {
                "type": prediction.prediction_type,
                "metric_name": prediction.metric_name,
                "current_value": round(prediction.current_value, 2),
                "predicted_breach_value": round(prediction.predicted_breach_value, 2),
                "eta_minutes": round(prediction.eta_minutes, 2),
                "confidence": round(prediction.confidence, 2),
                "growth_rate_per_minute": round(prediction.growth_rate_per_minute, 4),
                "explanation": prediction.explanation,
                "recommended_action": prediction.recommended_action
            }
        }
        
        # Add anomaly details if available
        if prediction.anomaly_result:
            event["anomaly"] = {
                "z_score": round(prediction.anomaly_result.z_score, 2),
                "severity": prediction.anomaly_result.severity,
                "baseline_mean": round(prediction.anomaly_result.baseline_mean, 2),
                "baseline_std": round(prediction.anomaly_result.baseline_std, 2),
                "explanation": prediction.anomaly_result.explanation
            }
        
        return event
    
    def _map_confidence_to_severity(self, confidence: float) -> str:
        """
        Map confidence score to severity level.
        
        Args:
            confidence: Confidence score (0-100)
            
        Returns:
            Severity level string
        """
        if confidence >= 95.0:
            return "critical"
        elif confidence >= 85.0:
            return "high"
        elif confidence >= 75.0:
            return "medium"
        else:
            return "low"
    
    async def push_prediction(self, prediction: Prediction) -> bool:
        """
        Push a single prediction to SDF.
        
        Args:
            prediction: Prediction to push
            
        Returns:
            True if successful, False otherwise
        """
        if self.mock_mode:
            # Mock mode - just log and return success
            event = self.format_prediction_event(prediction)
            print(f"[MOCK SDF] Would push event: {json.dumps(event, indent=2)}")
            return True
        
        event = self.format_prediction_event(prediction)
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    }
                    
                    response = await client.post(
                        self.sdf_endpoint,
                        json=event,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 201, 202]:
                        return True
                    
                    print(f"[SDF Bridge] Push failed with status {response.status_code}: {response.text}")
                    
                    # Retry on 5xx errors
                    if response.status_code >= 500 and attempt < self.max_retries - 1:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    
                    return False
                    
            except httpx.TimeoutException:
                print(f"[SDF Bridge] Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
                
            except Exception as e:
                print(f"[SDF Bridge] Error pushing to SDF: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return False
        
        return False
    
    async def push_predictions_batch(self, predictions: List[Prediction]) -> Dict[str, int]:
        """
        Push multiple predictions to SDF in batch.
        
        Args:
            predictions: List of predictions to push
            
        Returns:
            Dictionary with success/failure counts
        """
        if not predictions:
            return {"success": 0, "failed": 0}
        
        # Push all predictions concurrently
        tasks = [self.push_prediction(pred) for pred in predictions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if r is True)
        failed_count = len(results) - success_count
        
        return {
            "success": success_count,
            "failed": failed_count,
            "total": len(predictions)
        }
    
    def format_batch_events(self, predictions: List[Prediction]) -> List[Dict]:
        """
        Format multiple predictions as SDF events.
        
        Args:
            predictions: List of predictions
            
        Returns:
            List of formatted event dictionaries
        """
        return [self.format_prediction_event(pred) for pred in predictions]
