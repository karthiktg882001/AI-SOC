"""
Active Learning Service
Aggregates analyst feedback and prepares data for model retraining
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from database import SessionLocal
from models import Incident
from sqlalchemy import and_

class ActiveLearningService:
    """Service for managing active learning from analyst feedback"""
    
    def __init__(self):
        self.min_feedback_samples = 100  # Minimum samples needed for retraining
        self.retraining_interval_days = 7  # Retrain weekly
    
    def get_feedback_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get statistics on analyst feedback for active learning
        """
        db = SessionLocal()
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get all incidents with feedback
            incidents = db.query(Incident).filter(
                and_(
                    Incident.detected_at >= start_date,
                    Incident.raw_log_data.isnot(None)
                )
            ).all()
            
            total_incidents = len(incidents)
            with_feedback = 0
            true_positives = 0
            false_positives = 0
            no_feedback = 0
            
            feedback_samples = []
            
            for inc in incidents:
                if inc.raw_log_data and isinstance(inc.raw_log_data, dict):
                    feedback = inc.raw_log_data.get("analyst_feedback", {})
                    if feedback:
                        with_feedback += 1
                        feedback_type = feedback.get("feedback_type", "")
                        
                        if feedback_type == "true_positive":
                            true_positives += 1
                            feedback_samples.append({
                                'incident_id': inc.incident_id,
                                'label': 1,  # Malicious
                                'anomaly_score': inc.anomaly_score,
                                'features': self._extract_features_for_training(inc)
                            })
                        elif feedback_type == "false_positive":
                            false_positives += 1
                            feedback_samples.append({
                                'incident_id': inc.incident_id,
                                'label': 0,  # Benign
                                'anomaly_score': inc.anomaly_score,
                                'features': self._extract_features_for_training(inc)
                            })
                    else:
                        no_feedback += 1
            
            feedback_rate = (with_feedback / total_incidents * 100) if total_incidents > 0 else 0
            precision = (true_positives / (true_positives + false_positives)) if (true_positives + false_positives) > 0 else 0
            
            return {
                'total_incidents': total_incidents,
                'with_feedback': with_feedback,
                'no_feedback': no_feedback,
                'feedback_rate': round(feedback_rate, 2),
                'true_positives': true_positives,
                'false_positives': false_positives,
                'precision': round(precision, 2),
                'ready_for_retraining': len(feedback_samples) >= self.min_feedback_samples,
                'feedback_samples_count': len(feedback_samples),
                'feedback_samples': feedback_samples[:10]  # Return first 10 for preview
            }
        finally:
            db.close()
    
    def _extract_features_for_training(self, incident: Incident) -> Dict[str, Any]:
        """Extract features from incident for training"""
        # This would extract the same features used during detection
        # For now, return a simplified version
        return {
            'anomaly_score': incident.anomaly_score,
            'severity': incident.severity,
            'threat_type': incident.threat_type,
            'source_ip': incident.source_ip,
            'destination_ip': incident.destination_ip
        }
    
    def prepare_training_data(self, days: int = 90) -> Dict[str, Any]:
        """
        Prepare training data from feedback for model retraining
        """
        stats = self.get_feedback_statistics(days)
        
        if not stats['ready_for_retraining']:
            return {
                'ready': False,
                'message': f"Need {self.min_feedback_samples} feedback samples, have {stats['feedback_samples_count']}",
                'samples': stats['feedback_samples']
            }
        
        # Group by label
        positive_samples = [s for s in stats['feedback_samples'] if s['label'] == 1]
        negative_samples = [s for s in stats['feedback_samples'] if s['label'] == 0]
        
        return {
            'ready': True,
            'total_samples': len(stats['feedback_samples']),
            'positive_samples': len(positive_samples),
            'negative_samples': len(negative_samples),
            'class_balance': round(len(positive_samples) / len(stats['feedback_samples']), 2) if stats['feedback_samples'] else 0,
            'samples': stats['feedback_samples']
        }
    
    def should_retrain(self) -> bool:
        """Check if model should be retrained based on feedback"""
        stats = self.get_feedback_statistics(days=30)
        return stats['ready_for_retraining'] and stats['feedback_samples_count'] >= self.min_feedback_samples

# Global instance
active_learning_service = ActiveLearningService()

