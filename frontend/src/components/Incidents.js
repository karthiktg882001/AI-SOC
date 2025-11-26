import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { format } from 'date-fns';
import '../styles/modern-theme.css';
import './Incidents.css';

const API_URL = process.env.REACT_APP_API_URL || '';

function Incidents() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ status: '', severity: '' });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchIncidents();
  }, [filters]);

  const fetchIncidents = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.severity) params.append('severity', filters.severity);
      
      const response = await axios.get(`${API_URL}/api/incidents?${params.toString()}`);
      setIncidents(response.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const filteredIncidents = incidents.filter(incident => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      incident.threat_type?.toLowerCase().includes(searchLower) ||
      incident.description?.toLowerCase().includes(searchLower) ||
      incident.source_ip?.toLowerCase().includes(searchLower) ||
      incident.incident_id?.toLowerCase().includes(searchLower)
    );
  });

  if (loading) {
    return (
      <div className="modern-loading">
        <div className="modern-spinner"></div>
        <p>Loading security incidents...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="modern-error">
        <div className="error-icon">⚠️</div>
        <p>Error: {error}</p>
        <button className="modern-btn" onClick={fetchIncidents}>Retry</button>
      </div>
    );
  }

  return (
    <div className="modern-page">
      <div className="modern-container">
        {/* Header */}
        <div className="modern-page-header">
          <div>
            <h1 className="modern-page-title">
              <span className="modern-page-icon">🔍</span>
              <span>Security Incidents</span>
            </h1>
            <p className="modern-page-subtitle">Monitor and manage all security incidents</p>
          </div>
          <div className="modern-badge">{filteredIncidents.length} Total</div>
        </div>

        {/* Filters & Search */}
        <div className="modern-card">
          <div className="filters-modern">
            <div className="filter-group">
              <label>Search</label>
              <input
                type="text"
                className="modern-input"
                placeholder="Search by threat type, IP, or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="filter-group">
              <label>Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="modern-select"
              >
                <option value="">All Status</option>
                <option value="OPEN">Open</option>
                <option value="RESOLVED">Resolved</option>
                <option value="INVESTIGATING">Investigating</option>
              </select>
            </div>
            <div className="filter-group">
              <label>Severity</label>
              <select
                value={filters.severity}
                onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                className="modern-select"
              >
                <option value="">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>
        </div>

        {/* Incidents Grid */}
        {filteredIncidents.length === 0 ? (
          <div className="modern-card">
            <div className="empty-state">
              <div className="empty-icon">📋</div>
              <h3>No incidents found</h3>
              <p>No security incidents match your current filters.</p>
            </div>
          </div>
        ) : (
          <div className="incidents-grid-modern">
            {filteredIncidents.map((incident, index) => (
              <Link
                key={incident.incident_id}
                to={`/incidents/${incident.incident_id}`}
                className="incident-card-modern"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="incident-card-header-modern">
                  <div className="incident-id-modern">
                    <span className="id-icon">#</span>
                    {incident.incident_id.slice(0, 8)}
                  </div>
                  <span className={`status-badge-modern status-${incident.status.toLowerCase()}`}>
                    {incident.status}
                  </span>
                </div>
                <div className="incident-card-body-modern">
                  <h3 className="incident-title-modern">
                    {incident.threat_type || 'Unknown Threat'}
                  </h3>
                  <p className="incident-description-modern">
                    {incident.description || 'No description available'}
                  </p>
                  <div className="incident-meta-modern">
                    <span className={`severity-badge-modern severity-${incident.severity.toLowerCase()}`}>
                      {incident.severity}
                    </span>
                    <div className="meta-item">
                      <span className="meta-label">Score:</span>
                      <span className="meta-value">{(incident.anomaly_score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label">IP:</span>
                      <code className="ip-code">{incident.source_ip || 'N/A'}</code>
                    </div>
                  </div>
                </div>
                <div className="incident-card-footer-modern">
                  <span className="time-icon">🕐</span>
                  <span>{format(new Date(incident.detected_at), 'MMM dd, yyyy HH:mm')}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Incidents;
