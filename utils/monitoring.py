"""
Monitoring and metrics utilities for production deployment.
"""
import time
import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class Metrics:
    """Application metrics container."""
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    
    # System metrics
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    disk_usage_percent: float = 0.0
    
    # Vector store metrics
    vector_store_size: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    
    # Error tracking
    error_counts: Dict[str, int] = field(default_factory=dict)
    
    # Response times (for calculating averages)
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))

class MetricsCollector:
    """Collects and manages application metrics."""
    
    def __init__(self):
        self.metrics = Metrics()
        self.start_time = datetime.now()
        self.last_health_check = None
    
    def record_request(self, success: bool, response_time: float, error_type: Optional[str] = None):
        """Record a request and its outcome."""
        self.metrics.total_requests += 1
        
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
            if error_type:
                self.metrics.error_counts[error_type] = self.metrics.error_counts.get(error_type, 0) + 1
        
        # Update response time average
        self.metrics.response_times.append(response_time)
        self.metrics.average_response_time = sum(self.metrics.response_times) / len(self.metrics.response_times)
    
    def record_cache_event(self, hit: bool):
        """Record cache hit or miss."""
        if hit:
            self.metrics.cache_hits += 1
        else:
            self.metrics.cache_misses += 1
    
    def update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # Memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            self.metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
            
            # CPU usage
            self.metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
            
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            self.metrics.disk_usage_percent = (disk_usage.used / disk_usage.total) * 100
            
        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status."""
        self.update_system_metrics()
        
        uptime = datetime.now() - self.start_time
        
        # Calculate success rate
        success_rate = 0.0
        if self.metrics.total_requests > 0:
            success_rate = (self.metrics.successful_requests / self.metrics.total_requests) * 100
        
        # Determine health status
        health_status = "healthy"
        if success_rate < 90:
            health_status = "degraded"
        if success_rate < 70 or self.metrics.memory_usage_mb > 1000:
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.metrics.total_requests,
            "success_rate": success_rate,
            "average_response_time": self.metrics.average_response_time,
            "memory_usage_mb": self.metrics.memory_usage_mb,
            "cpu_usage_percent": self.metrics.cpu_usage_percent,
            "disk_usage_percent": self.metrics.disk_usage_percent,
            "error_counts": dict(self.metrics.error_counts),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        self.update_system_metrics()
        
        return {
            "requests": {
                "total": self.metrics.total_requests,
                "successful": self.metrics.successful_requests,
                "failed": self.metrics.failed_requests,
                "success_rate": (self.metrics.successful_requests / max(self.metrics.total_requests, 1)) * 100
            },
            "performance": {
                "average_response_time": self.metrics.average_response_time,
                "memory_usage_mb": self.metrics.memory_usage_mb,
                "cpu_usage_percent": self.metrics.cpu_usage_percent,
                "disk_usage_percent": self.metrics.disk_usage_percent
            },
            "cache": {
                "hits": self.metrics.cache_hits,
                "misses": self.metrics.cache_misses,
                "hit_rate": (self.metrics.cache_hits / max(self.metrics.cache_hits + self.metrics.cache_misses, 1)) * 100
            },
            "errors": dict(self.metrics.error_counts),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }

# Global metrics collector instance
metrics_collector = MetricsCollector()

def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector
