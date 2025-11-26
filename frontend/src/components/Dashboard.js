import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  PieChart, Pie, Cell, ResponsiveContainer, 
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  LineChart, Line
} from 'recharts';
import ProtectionDashboard from './ProtectionDashboard';
import './Dashboard.css';

const API_URL = process.env.REACT_APP_API_URL || '';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentThreats, setRecentThreats] = useState([]);
  const [activeIncidents, setActiveIncidents] = useState([]);
  const [zeroDayCount, setZeroDayCount] = useState(0);
  const [assetsAtRisk, setAssetsAtRisk] = useState([]);
  const [logTimeline, setLogTimeline] = useState([]);
  const [filterPresets, setFilterPresets] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState(null);
  const [sortBy, setSortBy] = useState('severity');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, [timeRange, sortBy]);

  useEffect(() => {
    fetchAnalystData();
    const interval = setInterval(fetchAnalystData, 30000);
    return () => clearInterval(interval);
  }, [sortBy]);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, threatsRes] = await Promise.all([
        axios.get(`${API_URL}/api/dashboard/stats`),
        axios.get(`${API_URL}/api/threats/recent?limit=10`)
      ]);
      setStats(statsRes.data);
      setRecentThreats(threatsRes.data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchAnalystData = async () => {
    try {
      const [activeIncidentsRes, zeroDayRes, assetsRes, timelineRes, presetsRes] = await Promise.all([
        axios.get(`${API_URL}/api/analyst/incidents/active?sort_by=${sortBy}&limit=20`),
        axios.get(`${API_URL}/api/analyst/zero-day/count`),
        axios.get(`${API_URL}/api/analyst/assets/at-risk?limit=5`),
        axios.get(`${API_URL}/api/analyst/log-volume/timeline?hours=24`),
        axios.get(`${API_URL}/api/analyst/filters/presets`)
      ]);
      setActiveIncidents(activeIncidentsRes.data);
      setZeroDayCount(zeroDayRes.data.zero_day_count);
      setAssetsAtRisk(assetsRes.data);
      setLogTimeline(timelineRes.data);
      setFilterPresets(presetsRes.data.presets);
    } catch (err) {
      console.error('Error fetching analyst data:', err);
    }
  };

  const handleFeedback = async (incidentId, feedbackType) => {
    try {
      await axios.post(`${API_URL}/api/analyst/incidents/${incidentId}/feedback`, {
        feedback_type: feedbackType,
        notes: ''
      });
      fetchAnalystData();
      alert(`Feedback submitted: ${feedbackType}`);
    } catch (err) {
      alert('Error submitting feedback');
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading security dashboard...</p>
      </div>
    );
  }

  if (error) return <div className="dashboard-error">Error: {error}</div>;
  if (!stats) return null;

  const severityData = [
    { name: 'Critical', value: stats.severity_breakdown.critical, color: '#ff4757', fill: 'url(#criticalGradient)' },
    { name: 'High', value: stats.severity_breakdown.high, color: '#ff6348', fill: 'url(#highGradient)' },
    { name: 'Medium', value: stats.severity_breakdown.medium, color: '#ffa502', fill: 'url(#mediumGradient)' },
    { name: 'Low', value: stats.severity_breakdown.low, color: '#2ed573', fill: 'url(#lowGradient)' }
  ];

  const threatTypeData = stats.top_threat_types.map(t => ({
    name: t.type || 'Unknown',
    count: t.count,
    fill: '#667eea'
  }));

  // Radar chart data
  const radarData = [
    { category: 'Malware', value: stats.severity_breakdown.critical * 10 },
    { category: 'Intrusion', value: stats.severity_breakdown.high * 10 },
    { category: 'Phishing', value: stats.severity_breakdown.medium * 10 },
    { category: 'DDoS', value: stats.severity_breakdown.low * 10 },
    { category: 'Data Exfil', value: (stats.severity_breakdown.critical + stats.severity_breakdown.high) * 5 }
  ];

  return (
    <div className="dashboard-modern">
      <div className="dashboard-container">
        {/* Header Section */}
        <div className="dashboard-header">
          <div className="header-content">
            <h1 className="dashboard-title">
              <span className="title-icon">🛡️</span>
              <span className="title-text">AI Security Operations Center</span>
            </h1>
            <p className="dashboard-subtitle">Real-time Threat Detection & Response</p>
          </div>
          <div className="header-actions">
            <select 
              className="time-range-selector" 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
        </div>

        {/* Zero-Day Indicator Card - High Visibility */}
        {zeroDayCount > 0 && (
          <div className="zero-day-alert">
            <div className="zero-day-content">
              <div className="zero-day-icon">⚠️</div>
              <div className="zero-day-text">
                <h3>Zero-Day Threats Detected</h3>
                <p>{zeroDayCount} unknown attack pattern{zeroDayCount > 1 ? 's' : ''} identified in the last 24 hours</p>
              </div>
              <div className="zero-day-count">{zeroDayCount}</div>
            </div>
          </div>
        )}

        {/* Key Metrics Cards */}
        <div className="metrics-grid">
          <div className="metric-card metric-critical">
            <div className="metric-icon-wrapper">
              <div className="metric-icon">🚨</div>
              <div className="metric-pulse"></div>
            </div>
            <div className="metric-content">
              <div className="metric-label">Total Incidents</div>
              <div className="metric-value">{stats.total_incidents}</div>
              <div className="metric-change positive">+{stats.recent_incidents_24h} today</div>
            </div>
          </div>

          <div className="metric-card metric-high">
            <div className="metric-icon-wrapper">
              <div className="metric-icon">⚠️</div>
            </div>
            <div className="metric-content">
              <div className="metric-label">Open Incidents</div>
              <div className="metric-value">{stats.status_breakdown.open}</div>
              <div className="metric-change warning">{stats.status_breakdown.resolved} resolved</div>
            </div>
          </div>

          <div className="metric-card metric-medium">
            <div className="metric-icon-wrapper">
              <div className="metric-icon">📊</div>
            </div>
            <div className="metric-content">
              <div className="metric-label">Last 24h</div>
              <div className="metric-value">{stats.recent_incidents_24h}</div>
              <div className="metric-change neutral">Active monitoring</div>
            </div>
          </div>

          <div className="metric-card metric-low">
            <div className="metric-icon-wrapper">
              <div className="metric-icon">📈</div>
            </div>
            <div className="metric-content">
              <div className="metric-label">Anomaly Score</div>
              <div className="metric-value">{(stats.average_anomaly_score * 100).toFixed(1)}%</div>
              <div className="metric-change positive">AI Confidence</div>
            </div>
          </div>
        </div>

        {/* 3D Charts Section */}
        <div className="charts-section">
          <div className="chart-card chart-3d">
            <div className="chart-header">
              <h3 className="chart-title">Threat Severity Distribution</h3>
              <div className="chart-badge">3D View</div>
            </div>
            <div className="chart-container-3d">
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <defs>
                    <linearGradient id="criticalGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ff4757" stopOpacity={1} />
                      <stop offset="100%" stopColor="#c44569" stopOpacity={0.8} />
                    </linearGradient>
                    <linearGradient id="highGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ff6348" stopOpacity={1} />
                      <stop offset="100%" stopColor="#c44569" stopOpacity={0.8} />
                    </linearGradient>
                    <linearGradient id="mediumGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#ffa502" stopOpacity={1} />
                      <stop offset="100%" stopColor="#ff6348" stopOpacity={0.8} />
                    </linearGradient>
                    <linearGradient id="lowGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#2ed573" stopOpacity={1} />
                      <stop offset="100%" stopColor="#1e8449" stopOpacity={0.8} />
                    </linearGradient>
                  </defs>
                  <Pie
                    data={severityData}
                    cx="50%"
                    cy="45%"
                    innerRadius={70}
                    outerRadius={110}
                    paddingAngle={8}
                    dataKey="value"
                    labelLine={false}
                  >
                    {severityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      background: 'rgba(26, 31, 58, 0.95)', 
                      border: '1px solid rgba(102, 126, 234, 0.3)',
                      borderRadius: '8px',
                      backdropFilter: 'blur(10px)'
                    }}
                    formatter={(value, name) => [`${value} incidents`, name]}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36}
                    formatter={(value, entry) => (
                      <span style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.85rem' }}>
                        {value}: {entry.payload.value} ({((entry.payload.value / severityData.reduce((sum, d) => sum + d.value, 0)) * 100).toFixed(0)}%)
                      </span>
                    )}
                    iconType="circle"
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card chart-3d">
            <div className="chart-header">
              <h3 className="chart-title">Top Threat Types</h3>
              <div className="chart-badge">3D View</div>
            </div>
            <div className="chart-container-3d">
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={threatTypeData}>
                  <defs>
                    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#667eea" stopOpacity={1} />
                      <stop offset="100%" stopColor="#764ba2" stopOpacity={0.8} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(102, 126, 234, 0.1)" />
                  <XAxis 
                    dataKey="name" 
                    stroke="rgba(255, 255, 255, 0.6)"
                    tick={{ fill: 'rgba(255, 255, 255, 0.7)' }}
                  />
                  <YAxis 
                    stroke="rgba(255, 255, 255, 0.6)"
                    tick={{ fill: 'rgba(255, 255, 255, 0.7)' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      background: 'rgba(26, 31, 58, 0.95)', 
                      border: '1px solid rgba(102, 126, 234, 0.3)',
                      borderRadius: '8px',
                      backdropFilter: 'blur(10px)'
                    }} 
                  />
                  <Bar 
                    dataKey="count" 
                    fill="url(#barGradient)"
                    radius={[8, 8, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="chart-card chart-3d">
          <div className="chart-header">
            <h3 className="chart-title">Threat Categories Analysis</h3>
            <div className="chart-badge">Radar View</div>
          </div>
          <div className="chart-container-3d">
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(102, 126, 234, 0.2)" />
                <PolarAngleAxis 
                  dataKey="category" 
                  tick={{ fill: 'rgba(255, 255, 255, 0.7)' }}
                />
                <PolarRadiusAxis 
                  angle={90} 
                  domain={[0, 100]}
                  tick={{ fill: 'rgba(255, 255, 255, 0.5)' }}
                />
                <Radar 
                  name="Threats" 
                  dataKey="value" 
                  stroke="#667eea" 
                  fill="#667eea" 
                  fillOpacity={0.6} 
                />
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(26, 31, 58, 0.95)', 
                    border: '1px solid rgba(102, 126, 234, 0.3)',
                    borderRadius: '8px',
                    backdropFilter: 'blur(10px)'
                  }} 
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Filter Bar */}
        <div className="quick-filter-bar">
          <div className="filter-label">Quick Filters:</div>
          <div className="filter-buttons">
            {filterPresets.map(preset => (
              <button
                key={preset.id}
                className={`filter-btn ${selectedFilter === preset.id ? 'active' : ''}`}
                onClick={() => setSelectedFilter(preset.id)}
              >
                {preset.name}
              </button>
            ))}
          </div>
          <select 
            className="sort-selector" 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="severity">Sort by Severity</option>
            <option value="mttr">Sort by MTTR</option>
            <option value="confidence">Sort by Confidence</option>
            <option value="detected_at">Sort by Date</option>
          </select>
        </div>

        {/* Top 5 Assets at Risk */}
        {assetsAtRisk.length > 0 && (
          <div className="chart-card">
            <div className="chart-header">
              <h3 className="chart-title">Top 5 Assets at Risk</h3>
              <div className="chart-badge">High Priority</div>
            </div>
            <div className="assets-risk-list">
              {assetsAtRisk.map((asset, index) => (
                <div key={index} className="asset-risk-item">
                  <div className="asset-rank">#{index + 1}</div>
                  <div className="asset-info">
                    <div className="asset-entity">
                      <span className="asset-type">{asset.entity_type}</span>
                      <code className="asset-value">{asset.entity_value}</code>
                    </div>
                    <div className="asset-metrics">
                      <span className="metric-badge">Incidents: {asset.incident_count}</span>
                      <span className="metric-badge">Avg Score: {(asset.avg_anomaly_score * 100).toFixed(1)}%</span>
                      <span className={`severity-badge severity-${asset.severity.toLowerCase()}`}>
                        {asset.severity}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Log Volume Timeline */}
        {logTimeline.length > 0 && (
          <div className="chart-card">
            <div className="chart-header">
              <h3 className="chart-title">Log Volume Timeline (24h)</h3>
              <div className="chart-badge">10K+ logs/sec</div>
            </div>
            <div className="chart-container-3d">
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={logTimeline}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(102, 126, 234, 0.1)" />
                  <XAxis 
                    dataKey="timestamp" 
                    stroke="rgba(255, 255, 255, 0.6)"
                    tick={{ fill: 'rgba(255, 255, 255, 0.7)', fontSize: 12 }}
                    tickFormatter={(value) => format(new Date(value), 'HH:mm')}
                  />
                  <YAxis 
                    stroke="rgba(255, 255, 255, 0.6)"
                    tick={{ fill: 'rgba(255, 255, 255, 0.7)' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      background: 'rgba(26, 31, 58, 0.95)', 
                      border: '1px solid rgba(102, 126, 234, 0.3)',
                      borderRadius: '8px'
                    }}
                    formatter={(value, name) => {
                      if (name === 'incident_count') return [`${value} incidents`, 'Incidents'];
                      if (name === 'estimated_log_volume') return [`~${value.toLocaleString()} logs`, 'Log Volume'];
                      return [value, name];
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="estimated_log_volume" 
                    stroke="#667eea" 
                    strokeWidth={2}
                    dot={{ fill: '#667eea', r: 4 }}
                    name="Log Volume"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="incident_count" 
                    stroke="#ff4757" 
                    strokeWidth={2}
                    dot={{ fill: '#ff4757', r: 4 }}
                    name="Incidents"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Active Incident Feed with Triage */}
        <div className="chart-card chart-fullwidth">
          <div className="chart-header">
            <h3 className="chart-title">Active Incident Feed</h3>
            <div className="chart-badge">{activeIncidents.length} Active</div>
          </div>
          <div className="threats-table-modern">
            <table>
              <thead>
                <tr>
                  <th>Threat Type</th>
                  <th>Severity</th>
                  <th>Confidence</th>
                  <th>MTTR</th>
                  <th>Mitigation</th>
                  <th>Zero-Day</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {activeIncidents.map((incident, index) => (
                  <tr key={incident.incident_id} style={{ animationDelay: `${index * 0.1}s` }}>
                    <td>
                      <div className="threat-type-cell">
                        <span className="threat-icon">🔍</span>
                        <span>{incident.threat_type || 'Unknown'}</span>
                      </div>
                    </td>
                    <td>
                      <span className={`severity-badge severity-${incident.severity.toLowerCase()}`}>
                        {incident.severity}
                      </span>
                    </td>
                    <td>
                      <div className="score-cell">
                        <div className="score-bar">
                          <div 
                            className="score-fill" 
                            style={{ width: `${(incident.confidence_score || 0) * 100}%` }}
                          ></div>
                        </div>
                        <span className="score-value">{((incident.confidence_score || 0) * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td>
                      <span className="mttr-badge">
                        {incident.mttr_hours.toFixed(1)}h
                      </span>
                    </td>
                    <td>
                      {incident.mitigation_ready ? (
                        <span className="mitigation-ready">✅ Ready</span>
                      ) : (
                        <span className="mitigation-pending">⏳ Pending</span>
                      )}
                    </td>
                    <td>
                      {incident.zero_day ? (
                        <span className="zero-day-badge">⚠️ Zero-Day</span>
                      ) : (
                        <span className="known-threat">✓ Known</span>
                      )}
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button 
                          className="btn-feedback btn-tp"
                          onClick={() => handleFeedback(incident.incident_id, 'true_positive')}
                          title="Mark as True Positive"
                        >
                          ✓ TP
                        </button>
                        <button 
                          className="btn-feedback btn-fp"
                          onClick={() => handleFeedback(incident.incident_id, 'false_positive')}
                          title="Mark as False Positive"
                        >
                          ✗ FP
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Threats Table */}
        <div className="chart-card chart-fullwidth">
          <div className="chart-header">
            <h3 className="chart-title">Recent Security Threats</h3>
            <div className="chart-badge">{recentThreats.length} Active</div>
          </div>
          <div className="threats-table-modern">
            <table>
              <thead>
                <tr>
                  <th>Threat Type</th>
                  <th>Severity</th>
                  <th>Source IP</th>
                  <th>Anomaly Score</th>
                  <th>Detected At</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentThreats.map((threat, index) => (
                  <tr key={threat.incident_id} style={{ animationDelay: `${index * 0.1}s` }}>
                    <td>
                      <div className="threat-type-cell">
                        <span className="threat-icon">🔍</span>
                        <span>{threat.threat_type || 'Unknown'}</span>
                      </div>
                    </td>
                    <td>
                      <span className={`severity-badge severity-${threat.severity.toLowerCase()}`}>
                        {threat.severity}
                      </span>
                    </td>
                    <td>
                      <code className="ip-address">{threat.source_ip || 'N/A'}</code>
                    </td>
                    <td>
                      <div className="score-cell">
                        <div className="score-bar">
                          <div 
                            className="score-fill" 
                            style={{ width: `${threat.anomaly_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="score-value">{(threat.anomaly_score * 100).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td>{format(new Date(threat.detected_at), 'MMM dd, HH:mm')}</td>
                    <td>
                      <span className={`status-badge status-${threat.status.toLowerCase()}`}>
                        {threat.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Active Protection Features - Moved to End */}
        <div className="active-features-section">
          <div className="section-divider">
            <span className="divider-text">Active Protection Features</span>
          </div>
          
          {/* Windows Security Style Protection Dashboard */}
          <ProtectionDashboard />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
