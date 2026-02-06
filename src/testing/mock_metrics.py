"""
Mock Metrics Generator - Testing utilities for Dynatrace API simulation.

This module provides mock data generators and a simulated Dynatrace API
for testing the prediction system without real infrastructure.
"""

import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import random


class MockMetricsGenerator:
    """
    Generates realistic mock metrics for testing.
    
    Supports various scenarios:
    - Normal baseline metrics (no anomalies)
    - CPU spikes
    - Cascading failures
    - Gradual degradation
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize mock metrics generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        np.random.seed(seed)
        random.seed(seed)
    
    def generate_normal_metrics(
        self,
        duration_hours: int = 24,
        interval_minutes: int = 5
    ) -> Dict[str, List[float]]:
        """
        Generate 24 hours of normal baseline metrics (no anomalies).
        
        Args:
            duration_hours: Duration in hours
            interval_minutes: Sampling interval in minutes
            
        Returns:
            Dictionary of metric_name -> list of values
        """
        num_points = (duration_hours * 60) // interval_minutes
        
        # CPU: 40-50% with small noise
        cpu_baseline = 45.0
        cpu_values = cpu_baseline + np.random.normal(0, 2.5, num_points)
        cpu_values = np.clip(cpu_values, 30, 60).tolist()
        
        # Memory: 55-65% with small noise
        mem_baseline = 60.0
        mem_values = mem_baseline + np.random.normal(0, 3.0, num_points)
        mem_values = np.clip(mem_values, 45, 75).tolist()
        
        # Disk: 70-80% with very small noise
        disk_baseline = 75.0
        disk_values = disk_baseline + np.random.normal(0, 1.5, num_points)
        disk_values = np.clip(disk_values, 65, 85).tolist()
        
        # Network: 20-30% with moderate noise
        network_baseline = 25.0
        network_values = network_baseline + np.random.normal(0, 3.5, num_points)
        network_values = np.clip(network_values, 10, 40).tolist()
        
        return {
            "cpu_utilization": cpu_values,
            "memory_utilization": mem_values,
            "disk_utilization": disk_values,
            "network_utilization": network_values
        }
    
    def generate_cpu_spike(
        self,
        baseline_hours: int = 24,
        severity: float = 0.8
    ) -> Dict[str, List[float]]:
        """
        Generate CPU spike scenario with configurable severity.
        
        Args:
            baseline_hours: Hours of baseline before spike
            severity: Spike severity (0.0-1.0), where 1.0 = critical
            
        Returns:
            Dictionary with CPU metrics showing spike
        """
        # Generate baseline
        baseline = self.generate_normal_metrics(duration_hours=baseline_hours)
        
        # Add spike at the end
        cpu_baseline = 45.0
        spike_value = cpu_baseline + (50.0 * severity)  # severity 0.8 -> ~69%
        
        # Append spike points (gradual ramp up)
        num_spike_points = 5
        spike_values = np.linspace(cpu_baseline + 5, spike_value, num_spike_points)
        
        baseline["cpu_utilization"].extend(spike_values.tolist())
        
        # Extend other metrics with normal values
        for key in ["memory_utilization", "disk_utilization", "network_utilization"]:
            last_value = baseline[key][-1]
            baseline[key].extend([last_value] * num_spike_points)
        
        return baseline
    
    def generate_cascading_failure(self) -> Dict[str, List[float]]:
        """
        Generate cascading failure scenario with multiple simultaneous anomalies.
        
        Returns:
            Dictionary with multiple metrics showing simultaneous spikes
        """
        # Start with baseline
        baseline = self.generate_normal_metrics(duration_hours=24)
        
        # Add simultaneous spikes to multiple metrics
        num_spike_points = 5
        
        # CPU spike: 45% -> 82%
        cpu_spike = np.linspace(50, 82, num_spike_points)
        baseline["cpu_utilization"].extend(cpu_spike.tolist())
        
        # Memory spike: 60% -> 88%
        mem_spike = np.linspace(65, 88, num_spike_points)
        baseline["memory_utilization"].extend(mem_spike.tolist())
        
        # Disk spike: 75% -> 91%
        disk_spike = np.linspace(78, 91, num_spike_points)
        baseline["disk_utilization"].extend(disk_spike.tolist())
        
        # Network spike: 25% -> 78%
        network_spike = np.linspace(30, 78, num_spike_points)
        baseline["network_utilization"].extend(network_spike.tolist())
        
        return baseline
    
    def generate_gradual_degradation(
        self,
        duration_hours: int = 6
    ) -> Dict[str, List[float]]:
        """
        Generate gradual degradation over hours (slow memory leak scenario).
        
        Args:
            duration_hours: Duration of degradation in hours
            
        Returns:
            Dictionary showing gradual memory increase
        """
        interval_minutes = 5
        num_points = (duration_hours * 60) // interval_minutes
        
        # Memory gradually increases from 55% to 92%
        mem_values = np.linspace(55, 92, num_points)
        mem_values += np.random.normal(0, 1.5, num_points)  # Add slight noise
        mem_values = np.clip(mem_values, 50, 95).tolist()
        
        # CPU gradually increases from 40% to 75%
        cpu_values = np.linspace(40, 75, num_points)
        cpu_values += np.random.normal(0, 2.0, num_points)
        cpu_values = np.clip(cpu_values, 35, 80).tolist()
        
        # Disk stays relatively stable
        disk_baseline = 75.0
        disk_values = disk_baseline + np.random.normal(0, 1.5, num_points)
        disk_values = np.clip(disk_values, 65, 85).tolist()
        
        # Network stays relatively stable
        network_baseline = 25.0
        network_values = network_baseline + np.random.normal(0, 3.5, num_points)
        network_values = np.clip(network_values, 10, 40).tolist()
        
        return {
            "cpu_utilization": cpu_values,
            "memory_utilization": mem_values,
            "disk_utilization": disk_values,
            "network_utilization": network_values
        }
    
    def get_latest_values(self, metrics: Dict[str, List[float]]) -> Dict[str, float]:
        """
        Get the latest value from each metric timeseries.
        
        Args:
            metrics: Dictionary of metric timeseries
            
        Returns:
            Dictionary of metric_name -> latest_value
        """
        return {name: values[-1] for name, values in metrics.items() if values}


class MockDynatraceAPI:
    """
    Mock Dynatrace API for testing.
    
    Simulates Dynatrace REST API responses with realistic metric data.
    """
    
    def __init__(self, metrics_generator: Optional[MockMetricsGenerator] = None):
        """
        Initialize mock Dynatrace API.
        
        Args:
            metrics_generator: MockMetricsGenerator instance (creates new if None)
        """
        self.generator = metrics_generator or MockMetricsGenerator()
        self.stored_metrics: Dict[str, Dict[str, List[float]]] = {}
    
    def load_scenario(self, scenario_name: str) -> None:
        """
        Load a pre-defined scenario.
        
        Args:
            scenario_name: Name of scenario (normal, cpu_spike, cascading, gradual)
        """
        if scenario_name == "normal":
            self.stored_metrics = self.generator.generate_normal_metrics()
        elif scenario_name == "cpu_spike":
            self.stored_metrics = self.generator.generate_cpu_spike(severity=0.8)
        elif scenario_name == "cascading":
            self.stored_metrics = self.generator.generate_cascading_failure()
        elif scenario_name == "gradual":
            self.stored_metrics = self.generator.generate_gradual_degradation()
        else:
            raise ValueError(f"Unknown scenario: {scenario_name}")
    
    def query_metrics(
        self,
        metric_names: List[str],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, List[float]]:
        """
        Query metrics from the mock API.
        
        Args:
            metric_names: List of metric names to query
            start_time: Start of time range (unused in mock)
            end_time: End of time range (unused in mock)
            
        Returns:
            Dictionary of metric_name -> values
        """
        if not self.stored_metrics:
            self.load_scenario("normal")
        
        result = {}
        for name in metric_names:
            if name in self.stored_metrics:
                result[name] = self.stored_metrics[name]
        
        return result
    
    def get_current_values(self) -> Dict[str, float]:
        """
        Get current (latest) values for all metrics.
        
        Returns:
            Dictionary of metric_name -> current_value
        """
        if not self.stored_metrics:
            self.load_scenario("normal")
        
        return self.generator.get_latest_values(self.stored_metrics)
    
    def get_baseline_values(
        self,
        metric_name: str,
        hours: int = 24
    ) -> List[float]:
        """
        Get baseline values for a metric (excluding recent spike).
        
        Args:
            metric_name: Name of the metric
            hours: Hours of baseline data
            
        Returns:
            List of baseline values
        """
        if not self.stored_metrics or metric_name not in self.stored_metrics:
            return []
        
        values = self.stored_metrics[metric_name]
        
        # Return all but last 5 points (excluding spike)
        if len(values) > 5:
            return values[:-5]
        
        return values
