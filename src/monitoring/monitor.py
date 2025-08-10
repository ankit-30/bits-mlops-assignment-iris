"""
Monitoring and logging utilities
"""
import logging
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelMonitor:
    """Class to handle model monitoring and metrics collection"""
    
    def __init__(self, db_path="logs/predictions.db"):
        self.db_path = db_path
        self.metrics = {
            'total_predictions': Counter('total_predictions', 'Total number of predictions made'),
            'prediction_latency': Histogram('prediction_latency_seconds', 'Prediction latency in seconds'),
            'prediction_confidence': Histogram('prediction_confidence', 'Model prediction confidence'),
            'class_distribution': Counter('class_predictions', 'Predictions by class', ['class_name']),
            'model_accuracy': Gauge('model_accuracy', 'Current model accuracy'),
        }
        
    def log_prediction_metrics(self, prediction_class, confidence, latency):
        """Log metrics for a prediction"""
        self.metrics['total_predictions'].inc()
        self.metrics['prediction_latency'].observe(latency)
        self.metrics['prediction_confidence'].observe(confidence)
        self.metrics['class_distribution'].labels(class_name=prediction_class).inc()
        
    def get_prediction_stats(self, days=7):
        """Get prediction statistics for the last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Calculate date threshold
            threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = """
                SELECT 
                    prediction,
                    COUNT(*) as count,
                    AVG(probability) as avg_confidence,
                    MIN(probability) as min_confidence,
                    MAX(probability) as max_confidence
                FROM predictions 
                WHERE timestamp > ?
                GROUP BY prediction
                ORDER BY count DESC
            """
            
            df = pd.read_sql_query(query, conn, params=[threshold_date])
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting prediction stats: {str(e)}")
            return []
    
    def get_hourly_prediction_volume(self, hours=24):
        """Get hourly prediction volume for the last N hours"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            threshold_date = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            query = """
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    COUNT(*) as prediction_count
                FROM predictions 
                WHERE timestamp > ?
                GROUP BY strftime('%Y-%m-%d %H:00:00', timestamp)
                ORDER BY hour
            """
            
            df = pd.read_sql_query(query, conn, params=[threshold_date])
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting hourly stats: {str(e)}")
            return []
    
    def check_data_drift(self, threshold=0.1):
        """Check for potential data drift in recent predictions"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get recent data (last 24 hours)
            recent_threshold = (datetime.now() - timedelta(hours=24)).isoformat()
            
            # Get historical baseline (7-30 days ago)
            baseline_start = (datetime.now() - timedelta(days=30)).isoformat()
            baseline_end = (datetime.now() - timedelta(days=7)).isoformat()
            
            recent_query = """
                SELECT sepal_length, sepal_width, petal_length, petal_width
                FROM predictions WHERE timestamp > ?
            """
            
            baseline_query = """
                SELECT sepal_length, sepal_width, petal_length, petal_width
                FROM predictions WHERE timestamp BETWEEN ? AND ?
            """
            
            recent_df = pd.read_sql_query(recent_query, conn, params=[recent_threshold])
            baseline_df = pd.read_sql_query(baseline_query, conn, params=[baseline_start, baseline_end])
            
            conn.close()
            
            if len(recent_df) == 0 or len(baseline_df) == 0:
                return {"status": "insufficient_data", "drift_detected": False}
            
            # Calculate feature means
            recent_means = recent_df.mean()
            baseline_means = baseline_df.mean()
            
            # Calculate relative change
            relative_changes = abs((recent_means - baseline_means) / baseline_means)
            
            # Check if any feature has drifted beyond threshold
            drift_detected = any(relative_changes > threshold)
            
            return {
                "status": "success",
                "drift_detected": drift_detected,
                "feature_changes": relative_changes.to_dict(),
                "threshold": threshold,
                "recent_samples": len(recent_df),
                "baseline_samples": len(baseline_df)
            }
            
        except Exception as e:
            logger.error(f"Error checking data drift: {str(e)}")
            return {"status": "error", "drift_detected": False, "error": str(e)}

class PerformanceMonitor:
    """Monitor API performance and system health"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
    def log_request(self, success=True):
        """Log API request"""
        self.request_count += 1
        if not success:
            self.error_count += 1
    
    def get_health_status(self):
        """Get current health status"""
        uptime = datetime.now() - self.start_time
        error_rate = self.error_count / max(self.request_count, 1)
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "status": "healthy" if error_rate < 0.05 else "degraded"
        }

def start_metrics_server(port=9090):
    """Start Prometheus metrics server"""
    try:
        start_http_server(port)
        logger.info(f"Metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {str(e)}")

def background_monitoring():
    """Background monitoring task"""
    monitor = ModelMonitor()
    
    while True:
        try:
            # Update model accuracy gauge (example)
            stats = monitor.get_prediction_stats(days=1)
            if stats:
                # Calculate average confidence as proxy for accuracy
                avg_confidence = sum(stat['avg_confidence'] for stat in stats) / len(stats)
                monitor.metrics['model_accuracy'].set(avg_confidence)
            
            # Check for data drift
            drift_info = monitor.check_data_drift()
            if drift_info.get('drift_detected'):
                logger.warning("Data drift detected!")
            
            time.sleep(300)  # Check every 5 minutes
            
        except Exception as e:
            logger.error(f"Error in background monitoring: {str(e)}")
            time.sleep(60)  # Retry after 1 minute on error

def start_background_monitoring():
    """Start background monitoring in a separate thread"""
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()
    logger.info("Background monitoring started")

if __name__ == "__main__":
    # Example usage
    monitor = ModelMonitor()
    
    # Get stats
    stats = monitor.get_prediction_stats()
    print("Prediction Stats:", json.dumps(stats, indent=2))
    
    # Get hourly volume
    volume = monitor.get_hourly_prediction_volume()
    print("Hourly Volume:", json.dumps(volume, indent=2))
    
    # Check drift
    drift = monitor.check_data_drift()
    print("Drift Check:", json.dumps(drift, indent=2))
