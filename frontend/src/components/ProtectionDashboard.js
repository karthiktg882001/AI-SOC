import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import './ProtectionDashboard.css';

const API_URL = process.env.REACT_APP_API_URL || '';

function ProtectionDashboard() {
  const [protectionStatus, setProtectionStatus] = useState(null);
  const [blockedThreats, setBlockedThreats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProtectionStatus();
    fetchBlockedThreats();
    
    // Real-time updates every 3 seconds
    const interval = setInterval(() => {
      fetchProtectionStatus();
      fetchBlockedThreats();
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const fetchProtectionStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/protection/status`);
      setProtectionStatus(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchBlockedThreats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/protection/threats-blocked`);
      setBlockedThreats(response.data);
    } catch (err) {
      console.error('Error fetching blocked threats:', err);
    }
  };

  const getProtectionIcon = (status) => {
    return status === "ACTIVE" ? "🛡️" : "⚠️";
  };

  const getProtectionColor = (status) => {
    return status === "ACTIVE" ? "#2ed573" : "#ff4757";
  };

  if (loading) return <div className="loading">Loading protection status...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!protectionStatus) return null;

  return (
    <div className="protection-dashboard">
      <div className="protection-header">
        <div className="protection-status-card">
          <div className="status-icon" style={{ color: getProtectionColor(protectionStatus.protection_status) }}>
            {getProtectionIcon(protectionStatus.protection_status)}
          </div>
          <div className="status-content">
            <h2>Real-Time Protection</h2>
            <p className={`status-text ${protectionStatus.protection_status.toLowerCase()}`}>
              {protectionStatus.protection_status}
            </p>
            <p className="status-subtext">
              Last updated: {format(new Date(protectionStatus.last_updated), 'HH:mm:ss')}
            </p>
          </div>
        </div>
      </div>

      <div className="protection-stats-grid">
        <div className="stat-card protection-stat">
          <div className="stat-icon">🚫</div>
          <div className="stat-content">
            <div className="stat-label">Threats Blocked Today</div>
            <div className="stat-value">{protectionStatus.protection_stats?.threats_blocked_today || 0}</div>
          </div>
        </div>

        <div className="stat-card protection-stat">
          <div className="stat-icon">🌐</div>
          <div className="stat-content">
            <div className="stat-label">IPs Blocked</div>
            <div className="stat-value">{protectionStatus.blocked_ips_count || 0}</div>
          </div>
        </div>

        <div className="stat-card protection-stat">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <div className="stat-label">Files Quarantined</div>
            <div className="stat-value">{protectionStatus.quarantined_files_count || 0}</div>
          </div>
        </div>

        <div className="stat-card protection-stat">
          <div className="stat-icon">⚡</div>
          <div className="stat-content">
            <div className="stat-label">Attacks Prevented</div>
            <div className="stat-value">{protectionStatus.protection_stats?.attacks_prevented || 0}</div>
          </div>
        </div>

        <div className="stat-card protection-stat">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <div className="stat-label">Critical Threats (24h)</div>
            <div className="stat-value critical">{protectionStatus.critical_threats_24h || 0}</div>
          </div>
        </div>

        <div className="stat-card protection-stat">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-label">Recent Threats (24h)</div>
            <div className="stat-value">{protectionStatus.recent_threats_24h || 0}</div>
          </div>
        </div>
      </div>

      <div className="protection-features">
        <h3 className="section-title">🛡️ Active Protection Features</h3>
        <div className="features-grid">
          {Object.entries(protectionStatus.active_protections || {}).map(([feature, enabled]) => (
            <div key={feature} className={`feature-item ${enabled ? 'enabled' : 'disabled'}`}>
              <div className="feature-icon">{enabled ? '✅' : '❌'}</div>
              <div className="feature-name">
                {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
            </div>
          ))}
        </div>
      </div>

      {blockedThreats && (
        <div className="blocked-threats-section">
          <h3 className="section-title">🚫 Blocked Threats</h3>
          <div className="blocked-items">
            <div className="blocked-item">
              <h4>Blocked IP Addresses ({blockedThreats.blocked_ips?.length || 0})</h4>
              <div className="blocked-list">
                {blockedThreats.blocked_ips && blockedThreats.blocked_ips.length > 0 ? (
                  blockedThreats.blocked_ips.slice(0, 10).map((ip, idx) => (
                    <span key={idx} className="blocked-tag">{ip}</span>
                  ))
                ) : (
                  <p className="no-items">No IPs blocked</p>
                )}
              </div>
            </div>

            <div className="blocked-item">
              <h4>Blocked Ports ({blockedThreats.blocked_ports?.length || 0})</h4>
              <div className="blocked-list">
                {blockedThreats.blocked_ports && blockedThreats.blocked_ports.length > 0 ? (
                  blockedThreats.blocked_ports.slice(0, 10).map((port, idx) => (
                    <span key={idx} className="blocked-tag">{port}</span>
                  ))
                ) : (
                  <p className="no-items">No ports blocked</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {protectionStatus.protection_stats?.last_blocked_at && (
        <div className="last-action">
          <p className="last-action-text">
            Last threat blocked: {format(new Date(protectionStatus.protection_stats.last_blocked_at), 'MMM dd, yyyy HH:mm:ss')}
          </p>
        </div>
      )}
    </div>
  );
}

export default ProtectionDashboard;

