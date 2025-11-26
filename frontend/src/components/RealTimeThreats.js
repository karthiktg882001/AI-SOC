import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';
import './RealTimeThreats.css';

const API_URL = process.env.REACT_APP_API_URL || '';

function RealTimeThreats() {
  const [liveThreats, setLiveThreats] = useState([]);
  const [threatStats, setThreatStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLiveThreats();
    fetchThreatStats();
    
    // Real-time updates every 5 seconds
    const interval = setInterval(() => {
      fetchLiveThreats();
      fetchThreatStats();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchLiveThreats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auto-threat/live-threats?limit=10`);
      setLiveThreats(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchThreatStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auto-threat/threat-stats`);
      setThreatStats(response.data);
    } catch (err) {
      console.error('Error fetching threat stats:', err);
      // Add user-friendly error display logic here
      if (err.response && err.response.status === 500) {
        // Example: set an error state to display to the user
        // setError('Failed to load threat statistics. Please try again later.');
      } else {
        // setError('An unexpected error occurred.');
      }
    }
  };


  const getSeverityClass = (severity) => {
    return `severity-${severity.toLowerCase()}`;
  };

  const getThreatIcon = (threatType) => {
    const icons = {
      'zero_day': '🆕',
      'ransomware': '🔒',
      'data_exfiltration': '📤',
      'advanced_persistent_threat': '🕵️',
      'iot_attack': '📱',
      'cloud_breach': '☁️',
      'brute_force': '🔨',
      'port_scan': '🔍',
      'malware': '🦠',
      'ddos': '💥',
      'sql_injection': '💉',
      'xss': '⚠️'
    };
    return icons[threatType] || '🚨';
  };

  if (loading && liveThreats.length === 0) {
    return <div className="loading">Loading real-time threats...</div>;
  }

  if (error && liveThreats.length === 0) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="realtime-threats">
      <div className="threats-header">
        <h2>🔴 Live Threat Detection</h2>
        {threatStats && (
          <div className="threat-stats-badge">
            <span className="stat-item">
              <strong>{threatStats.last_24h_detections}</strong> Last 24h
            </span>
            <span className="stat-item">
              <strong>{threatStats.zero_day_detections}</strong> Zero-day
            </span>
            <span className="stat-item">
              <strong>{threatStats.critical_threats}</strong> Critical
            </span>
          </div>
        )}
      </div>

      {liveThreats.length === 0 ? (
        <div className="no-threats">
          <div className="no-threats-icon">✅</div>
          <p>No active threats detected in the last hour</p>
          <p className="subtext">System is monitoring in real-time</p>
        </div>
      ) : (
        <div className="threats-list">
          {liveThreats.map((threat) => (
            <Link
              key={threat.incident_id}
              to={`/incidents/${threat.incident_id}`}
              className="threat-card"
            >
              <div className="threat-icon">{getThreatIcon(threat.threat_type)}</div>
              <div className="threat-content">
                <div className="threat-header">
                  <h3 className="threat-type">{threat.threat_type.replace('_', ' ').toUpperCase()}</h3>
                  <span className={`severity-badge ${getSeverityClass(threat.severity)}`}>
                    {threat.severity}
                  </span>
                </div>
                <div className="threat-details">
                  <div className="detail-item">
                    <span className="detail-label">Source IP:</span>
                    <span className="detail-value">{threat.source_ip || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Anomaly Score:</span>
                    <span className="detail-value score">{(threat.anomaly_score * 100).toFixed(1)}%</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Detected:</span>
                    <span className="detail-value">
                      {format(new Date(threat.detected_at), 'HH:mm:ss')}
                    </span>
                  </div>
                </div>
                <p className="threat-description">{threat.description}</p>
              </div>
              <div className="threat-arrow">→</div>
            </Link>
          ))}
        </div>
      )}

      <div className="threats-footer">
        <p className="update-info">
          🔄 Auto-updating every 5 seconds • Powered by Deep Learning & Generative AI
        </p>
      </div>
    </div>
  );
}

export default RealTimeThreats;

