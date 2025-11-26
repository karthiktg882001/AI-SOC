"""
Explainable AI (XAI) Service using SHAP
Provides feature importance explanations for anomaly detection
"""
import numpy as np
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("⚠️  SHAP not available. XAI explanations will be limited.")

class XAIExplainer:
    """Service for generating explainable AI explanations"""
    
    def __init__(self):
        self.explainer = None
        self.feature_names = [
            'protocol_entropy', 'port_entropy', 'ip_entropy', 'message_length',
            'timestamp_variance', 'source_ip_count', 'destination_ip_count',
            'unique_ports', 'connection_count', 'error_rate',
            'http_method_diversity', 'user_agent_diversity', 'status_code_diversity',
            'request_size_avg', 'response_size_avg', 'latency_avg',
            'geolocation_risk', 'time_of_day', 'day_of_week',
            'session_duration', 'data_transfer_rate'
        ]
        self.background_data = None
        self._initialize_explainer()
    
    def _initialize_explainer(self):
        """Initialize SHAP explainer with background data"""
        if not SHAP_AVAILABLE:
            return
        
        try:
            # Create synthetic background data for explanation
            # In production, this would be sampled from historical logs
            np.random.seed(42)
            self.background_data = np.random.rand(100, len(self.feature_names)) * 0.5
            
            # Use TreeExplainer for tree-based models or KernelExplainer for any model
            # For now, use KernelExplainer as it works with any model
            self.explainer = shap.KernelExplainer(
                self._model_predict_wrapper,
                self.background_data
            )
            print("✅ XAI Explainer initialized with SHAP")
        except Exception as e:
            print(f"⚠️  Could not initialize SHAP explainer: {e}")
            self.explainer = None
    
    def _model_predict_wrapper(self, features: np.ndarray) -> np.ndarray:
        """
        Wrapper function for model prediction
        This simulates model predictions - in production, use actual model
        """
        # Simplified prediction: higher values = more anomalous
        # In production, this would call the actual anomaly detection model
        anomaly_scores = np.mean(features, axis=1) + np.std(features, axis=1) * 0.5
        return anomaly_scores.reshape(-1, 1)
    
    def explain_anomaly(self, features: np.ndarray, anomaly_score: float) -> Dict[str, Any]:
        """
        Generate explanation for an anomaly detection result
        
        Args:
            features: Feature vector (1D array)
            anomaly_score: The anomaly score from detection
            
        Returns:
            Dictionary with explanation data
        """
        if not SHAP_AVAILABLE or self.explainer is None:
            return self._fallback_explanation(features, anomaly_score)
        
        try:
            # Ensure features is 2D
            if len(features.shape) == 1:
                features = features.reshape(1, -1)
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(features[0])
            
            # Get feature importance
            feature_importance = {}
            for i, feature_name in enumerate(self.feature_names):
                if i < len(shap_values):
                    feature_importance[feature_name] = {
                        'shap_value': float(shap_values[i]),
                        'contribution': float(shap_values[i]),
                        'abs_contribution': abs(float(shap_values[i]))
                    }
            
            # Sort by absolute contribution
            sorted_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1]['abs_contribution'],
                reverse=True
            )
            
            # Get top contributing features
            top_features = [
                {
                    'feature': name,
                    'contribution': data['contribution'],
                    'percentage': abs(data['contribution']) / sum(abs(f['contribution']) for f in feature_importance.values()) * 100 if sum(abs(f['contribution']) for f in feature_importance.values()) > 0 else 0
                }
                for name, data in sorted_features[:5]
            ]
            
            # Calculate confidence breakdown
            positive_contributors = [f for f in sorted_features if f[1]['contribution'] > 0]
            negative_contributors = [f for f in sorted_features if f[1]['contribution'] < 0]
            
            return {
                'anomaly_score': float(anomaly_score),
                'explanation_method': 'SHAP',
                'top_contributing_features': top_features,
                'positive_contributors': [
                    {'feature': name, 'contribution': data['contribution']}
                    for name, data in positive_contributors[:3]
                ],
                'negative_contributors': [
                    {'feature': name, 'contribution': data['contribution']}
                    for name, data in negative_contributors[:3]
                ],
                'feature_importance': feature_importance,
                'explanation_summary': self._generate_summary(top_features, anomaly_score)
            }
        except Exception as e:
            print(f"Error generating SHAP explanation: {e}")
            return self._fallback_explanation(features, anomaly_score)
    
    def _fallback_explanation(self, features: np.ndarray, anomaly_score: float) -> Dict[str, Any]:
        """Fallback explanation when SHAP is not available"""
        # Simple feature-based explanation
        feature_values = {}
        for i, name in enumerate(self.feature_names):
            if i < len(features):
                feature_values[name] = float(features[i])
        
        # Identify high-value features
        high_features = [
            {'feature': name, 'value': val, 'contribution': val * 0.1}
            for name, val in sorted(feature_values.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        ]
        
        return {
            'anomaly_score': float(anomaly_score),
            'explanation_method': 'Feature Analysis',
            'top_contributing_features': high_features,
            'explanation_summary': f"Anomaly score {anomaly_score:.2f} based on feature analysis. Top contributors: {', '.join([f['feature'] for f in high_features[:3]])}"
        }
    
    def _generate_summary(self, top_features: List[Dict], anomaly_score: float) -> str:
        """Generate human-readable explanation summary"""
        if not top_features:
            return f"Anomaly detected with score {anomaly_score:.2f}"
        
        top_3 = top_features[:3]
        feature_names = [f['feature'].replace('_', ' ').title() for f in top_3]
        contributions = [f['contribution'] for f in top_3]
        
        summary = f"Anomaly score {anomaly_score:.2f}, primarily driven by: "
        parts = []
        for name, contrib in zip(feature_names, contributions):
            direction = "high" if contrib > 0 else "low"
            parts.append(f"{direction} {name} ({abs(contrib):.3f})")
        
        summary += ", ".join(parts)
        return summary
    
    def explain_feature_importance(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features from log data and generate explanation
        """
        from services.anomaly_detector import AnomalyDetector
        
        detector = AnomalyDetector()
        features = detector.extract_features(log_data)
        
        # Get anomaly score
        is_anomaly, anomaly_score, _ = detector.detect_anomaly(log_data)
        
        return self.explain_anomaly(features, anomaly_score)

# Global instance
xai_explainer = XAIExplainer()

