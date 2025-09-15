"""
Unit tests for monitoring utilities.
"""
import pytest
import time
from utils.monitoring import MetricsCollector, Metrics

class TestMetricsCollector:
    """Test cases for metrics collection."""
    
    def test_initial_metrics(self):
        """Test initial metrics state."""
        collector = MetricsCollector()
        assert collector.metrics.total_requests == 0
        assert collector.metrics.successful_requests == 0
        assert collector.metrics.failed_requests == 0
    
    def test_record_successful_request(self):
        """Test recording successful request."""
        collector = MetricsCollector()
        collector.record_request(success=True, response_time=1.5)
        
        assert collector.metrics.total_requests == 1
        assert collector.metrics.successful_requests == 1
        assert collector.metrics.failed_requests == 0
        assert collector.metrics.average_response_time == 1.5
    
    def test_record_failed_request(self):
        """Test recording failed request."""
        collector = MetricsCollector()
        collector.record_request(success=False, response_time=2.0, error_type="ConnectionError")
        
        assert collector.metrics.total_requests == 1
        assert collector.metrics.successful_requests == 0
        assert collector.metrics.failed_requests == 1
        assert collector.metrics.error_counts["ConnectionError"] == 1
    
    def test_record_multiple_requests(self):
        """Test recording multiple requests."""
        collector = MetricsCollector()
        
        # Record multiple requests
        collector.record_request(success=True, response_time=1.0)
        collector.record_request(success=True, response_time=2.0)
        collector.record_request(success=False, response_time=3.0, error_type="TimeoutError")
        
        assert collector.metrics.total_requests == 3
        assert collector.metrics.successful_requests == 2
        assert collector.metrics.failed_requests == 1
        assert collector.metrics.average_response_time == 2.0
        assert collector.metrics.error_counts["TimeoutError"] == 1
    
    def test_record_cache_events(self):
        """Test recording cache events."""
        collector = MetricsCollector()
        
        collector.record_cache_event(hit=True)
        collector.record_cache_event(hit=True)
        collector.record_cache_event(hit=False)
        
        assert collector.metrics.cache_hits == 2
        assert collector.metrics.cache_misses == 1
    
    def test_health_status_healthy(self):
        """Test health status when healthy."""
        collector = MetricsCollector()
        
        # Record some successful requests
        for _ in range(10):
            collector.record_request(success=True, response_time=1.0)
        
        health = collector.get_health_status()
        assert health["status"] == "healthy"
        assert health["success_rate"] == 100.0
    
    def test_health_status_degraded(self):
        """Test health status when degraded."""
        collector = MetricsCollector()
        
        # Record mostly successful requests (80% success rate)
        for _ in range(8):
            collector.record_request(success=True, response_time=1.0)
        for _ in range(2):
            collector.record_request(success=False, response_time=1.0)
        
        health = collector.get_health_status()
        assert health["status"] == "degraded"
        assert health["success_rate"] == 80.0
    
    def test_health_status_unhealthy(self):
        """Test health status when unhealthy."""
        collector = MetricsCollector()
        
        # Record mostly failed requests (30% success rate)
        for _ in range(3):
            collector.record_request(success=True, response_time=1.0)
        for _ in range(7):
            collector.record_request(success=False, response_time=1.0)
        
        health = collector.get_health_status()
        assert health["status"] == "unhealthy"
        assert health["success_rate"] == 30.0
