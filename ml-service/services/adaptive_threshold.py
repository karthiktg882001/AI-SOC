"""
Adaptive Threshold Service
Dynamically adjusts anomaly detection thresholds based on context
"""
from datetime import datetime, timedelta
from typing import Dict, Any
import statistics

class AdaptiveThresholdService:
    """Service for calculating adaptive anomaly detection thresholds"""
    
    def __init__(self):
        self.base_threshold = 0.7  # Default threshold
        self.min_threshold = 0.5   # Minimum threshold (high sensitivity)
        self.max_threshold = 0.9   # Maximum threshold (low sensitivity)
        
        # Historical data (in production, this would be in database)
        self.hourly_patterns = {}  # hour -> average_anomaly_score
        self.weekly_patterns = {}  # day_of_week -> average_anomaly_score
        self.false_positive_rate = 0.0
        
    def get_threshold(self, context: Dict[str, Any] = None) -> float:
        """
        Get adaptive threshold based on current context
        Context can include:
        - current_hour: int (0-23)
        - day_of_week: int (0-6, Monday=0)
        - recent_false_positive_rate: float
        - network_load: float (0-1)
        - recent_incident_count: int
        """
        if context is None:
            context = self._get_default_context()
        
        threshold = self.base_threshold
        
        # Adjust based on time of day
        current_hour = context.get('current_hour', datetime.now().hour)
        if 2 <= current_hour <= 6:  # Quiet hours (2 AM - 6 AM)
            threshold -= 0.1  # Lower threshold = higher sensitivity
        elif 9 <= current_hour <= 17:  # Business hours
            threshold += 0.05  # Slightly higher threshold = reduce false positives
        
        # Adjust based on day of week
        day_of_week = context.get('day_of_week', datetime.now().weekday())
        if day_of_week >= 5:  # Weekend
            threshold -= 0.05  # Lower threshold on weekends
        
        # Adjust based on false positive rate
        fpr = context.get('recent_false_positive_rate', self.false_positive_rate)
        if fpr > 0.1:  # High false positive rate (>10%)
            threshold += 0.1  # Increase threshold to reduce FPR
        elif fpr < 0.02:  # Low false positive rate (<2%)
            threshold -= 0.05  # Decrease threshold to catch more
        
        # Adjust based on network load
        network_load = context.get('network_load', 0.5)
        if network_load > 0.8:  # High network load
            threshold += 0.05  # Slightly higher threshold during high load
        
        # Adjust based on recent incident count
        recent_incidents = context.get('recent_incident_count', 0)
        if recent_incidents > 50:  # Many recent incidents
            threshold += 0.1  # Higher threshold to reduce alert fatigue
        
        # Clamp threshold to valid range
        threshold = max(self.min_threshold, min(self.max_threshold, threshold))
        
        return round(threshold, 2)
    
    def update_false_positive_rate(self, fpr: float):
        """Update the false positive rate for threshold adjustment"""
        self.false_positive_rate = fpr
    
    def update_hourly_pattern(self, hour: int, avg_score: float):
        """Update hourly pattern data"""
        self.hourly_patterns[hour] = avg_score
    
    def update_weekly_pattern(self, day: int, avg_score: float):
        """Update weekly pattern data"""
        self.weekly_patterns[day] = avg_score
    
    def _get_default_context(self) -> Dict[str, Any]:
        """Get default context from current time"""
        now = datetime.now()
        return {
            'current_hour': now.hour,
            'day_of_week': now.weekday(),
            'recent_false_positive_rate': self.false_positive_rate,
            'network_load': 0.5,  # Default
            'recent_incident_count': 0  # Default
        }
    
    def get_severity_from_score(self, anomaly_score: float, context: Dict[str, Any] = None) -> str:
        """
        Determine severity based on anomaly score and adaptive threshold
        """
        threshold = self.get_threshold(context)
        
        if anomaly_score >= threshold + 0.2:
            return "CRITICAL"
        elif anomaly_score >= threshold + 0.1:
            return "HIGH"
        elif anomaly_score >= threshold:
            return "MEDIUM"
        else:
            return "LOW"

# Global instance
adaptive_threshold_service = AdaptiveThresholdService()

