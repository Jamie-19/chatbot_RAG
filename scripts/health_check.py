#!/usr/bin/env python3
"""
Health check script for monitoring and alerting.
"""
import sys
import json
import requests
from datetime import datetime

def check_health():
    """Check application health and return status."""
    try:
        # Import here to avoid circular imports
        from main import handle_health
        from utils.monitoring import get_metrics_collector
        
        metrics = get_metrics_collector()
        health_status = metrics.get_health_status()
        
        # Determine exit code based on health
        if health_status['status'] == 'healthy':
            print("Application is healthy")
            return 0
        elif health_status['status'] == 'degraded':
            print("Application is degraded")
            return 1
        else:
            print("Application is unhealthy")
            return 2
            
    except Exception as e:
        print(f"Health check failed: {e}")
        return 3

def send_alert(webhook_url: str, message: str):
    """Send alert to webhook (e.g., Slack, Discord)."""
    try:
        payload = {
            "text": f"RAG Chatbot Alert: {message}",
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send alert: {e}")

if __name__ == "__main__":
    exit_code = check_health()
    
    # Send alert if unhealthy
    if exit_code >= 2:
        webhook_url = sys.argv[1] if len(sys.argv) > 1 else None
        if webhook_url:
            send_alert(webhook_url, "Application is unhealthy")
    
    sys.exit(exit_code)
