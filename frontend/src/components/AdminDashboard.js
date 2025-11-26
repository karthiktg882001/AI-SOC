import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { useAuth } from '../hooks/useAuth';
import ChatAssistant from './ChatAssistant';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, LineChart, Line } from 'recharts';
import '../styles/modern-theme.css';
import './AdminDashboard.css';

const API_URL = process.env.REACT_APP_API_URL || '';

function AdminDashboard() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [userAnalytics, setUserAnalytics] = useState(null);
  const [activityAnalytics, setActivityAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [editingUser, setEditingUser] = useState(null);
  const [newUser, setNewUser] = useState({ email: '', name: '', password: '', is_admin: false, role: 'user' });
  const [supportStats, setSupportStats] = useState(null);
  const [selectedChatUser, setSelectedChatUser] = useState(null);
  const [userMessages, setUserMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [usersWithMessages, setUsersWithMessages] = useState([]);
  const [supportRequests, setSupportRequests] = useState([]);
  
  // KPI states
  const [mttdMttrTrends, setMttdMttrTrends] = useState(null);
  const [falsePositiveRate, setFalsePositiveRate] = useState(null);
  const [detectionAccuracy, setDetectionAccuracy] = useState(null);
  const [incidentVolumeByCategory, setIncidentVolumeByCategory] = useState(null);
  const [serviceHealth, setServiceHealth] = useState(null);
  const [logIngestionStatus, setLogIngestionStatus] = useState(null);
  const [complianceReadiness, setComplianceReadiness] = useState(null);
  const [resourceUsage, setResourceUsage] = useState(null);
  
  // Search and filter states
  const [userSearch, setUserSearch] = useState('');
  const [incidentSearch, setIncidentSearch] = useState('');
  const [userRoleFilter, setUserRoleFilter] = useState('ALL');
  const [incidentSeverityFilter, setIncidentSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30); // seconds

  // Real-time refresh
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      if (activeTab === 'overview') {
        fetchStats();
        fetchKPIData();
      }
      if (activeTab === 'users') fetchUsers();
      if (activeTab === 'incidents') fetchIncidents();
      if (activeTab === 'analytics') {
        fetchUserAnalytics();
        fetchActivityAnalytics();
      }
      if (activeTab === 'support') {
        fetchSupportRequests();
        fetchSupportStats();
        fetchUsersWithMessages();
      }
    }, refreshInterval * 1000);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, activeTab]);

  useEffect(() => {
    if (activeTab === 'overview') {
      fetchStats();
      fetchKPIData();
    } else if (activeTab === 'users') {
      fetchUsers();
    } else if (activeTab === 'incidents') {
      fetchIncidents();
    } else if (activeTab === 'analytics') {
      fetchUserAnalytics();
      fetchActivityAnalytics();
    } else if (activeTab === 'support') {
      fetchSupportRequests();
      fetchSupportStats();
      fetchUsersWithMessages();
    }
  }, [activeTab, statusFilter]);

  const fetchKPIData = async () => {
    try {
      const [
        trendsRes,
        fprRes,
        accuracyRes,
        volumeRes,
        healthRes,
        logStatusRes,
        complianceRes,
        resourceRes
      ] = await Promise.all([
        axios.get(`${API_URL}/api/kpi/mttd-mttr/trends?days=30`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/kpi/false-positive-rate?days=30`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/kpi/detection-accuracy?days=30`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/kpi/incident-volume/by-category?days=30`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/kpi/service-health`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/kpi/log-ingestion/status`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/kpi/compliance/readiness?framework=NIST`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/kpi/resource-usage`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setMttdMttrTrends(trendsRes.data);
      setFalsePositiveRate(fprRes.data);
      setDetectionAccuracy(accuracyRes.data);
      setIncidentVolumeByCategory(volumeRes.data);
      setServiceHealth(healthRes.data);
      setLogIngestionStatus(logStatusRes.data);
      setComplianceReadiness(complianceRes.data);
      setResourceUsage(resourceRes.data);
    } catch (err) {
      console.error('Error fetching KPI data:', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'support' && selectedChatUser) {
      setUserMessages([]);
      setChatInput('');
      fetchUserMessages(selectedChatUser.id);
      const interval = setInterval(() => {
        if (selectedChatUser) {
          fetchUserMessages(selectedChatUser.id);
        }
      }, 5000);
      return () => clearInterval(interval);
    } else if (activeTab === 'support' && !selectedChatUser) {
      setUserMessages([]);
      setChatInput('');
    }
  }, [activeTab, selectedChatUser?.id]);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/admin/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to fetch statistics' });
    }
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/admin/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUsers(response.data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to fetch users' });
    } finally {
      setLoading(false);
    }
  };

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/api/incidents`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIncidents(response.data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to fetch incidents' });
    } finally {
      setLoading(false);
    }
  };

  const fetchUserAnalytics = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/admin/analytics/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserAnalytics(response.data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to fetch user analytics' });
    }
  };

  const fetchActivityAnalytics = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/admin/analytics/activity?days=30`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setActivityAnalytics(response.data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to fetch activity analytics' });
    }
  };

  const fetchSupportRequests = async () => {
    setLoading(true);
    try {
      const url = statusFilter !== 'ALL' 
        ? `${API_URL}/api/chat/admin/support/requests?status_filter=${statusFilter}`
        : `${API_URL}/api/chat/admin/support/requests`;
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSupportRequests(response.data || []);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to fetch support requests' });
    } finally {
      setLoading(false);
    }
  };

  const fetchSupportStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/chat/admin/support/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSupportStats(response.data);
    } catch (err) {
      console.error('Failed to fetch support stats:', err);
    }
  };

  const fetchUsersWithMessages = async () => {
    try {
      const [usersRes, requestsRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/users`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/api/chat/admin/support/requests`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      const allUsers = usersRes.data;
      const allRequests = requestsRes.data;
      const userIdsWithRequests = [...new Set(allRequests.map(r => r.user_id))];
      
      const usersWithData = allUsers
        .filter(u => userIdsWithRequests.includes(u.id))
        .map(user => {
          const userRequests = allRequests.filter(r => r.user_id === user.id);
          const unreadCount = userRequests.filter(r => !r.response && (r.status === 'PENDING' || r.status === 'IN_PROGRESS')).length;
          const lastMessage = userRequests.length > 0 
            ? userRequests[0].message.substring(0, 50) + '...'
            : 'No messages';
          const lastMessageTime = userRequests.length > 0 
            ? userRequests[0].created_at 
            : null;
          
          return {
            ...user,
            unreadCount,
            lastMessage,
            lastMessageTime,
            requestCount: userRequests.length
          };
        })
        .sort((a, b) => {
          if (a.unreadCount !== b.unreadCount) {
            return b.unreadCount - a.unreadCount;
          }
          if (a.lastMessageTime && b.lastMessageTime) {
            return new Date(b.lastMessageTime) - new Date(a.lastMessageTime);
          }
          return 0;
        });
      
      setUsersWithMessages(usersWithData);
    } catch (err) {
      console.error('Failed to fetch users with messages:', err);
    }
  };

  const fetchUserMessages = async (userId) => {
    if (!userId) return;
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/chat/admin/user/${userId}/messages`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (selectedChatUser && selectedChatUser.id === userId) {
        setUserMessages(response.data.messages || []);
        setSelectedChatUser(prev => {
          if (prev && prev.id === userId) {
            return {
              ...prev,
              ...response.data.user,
              unreadCount: response.data.unread_count
            };
          }
          return prev;
        });
      }
    } catch (err) {
      console.error('Failed to fetch user messages:', err);
      if (selectedChatUser && selectedChatUser.id === userId) {
        setMessage({ type: 'error', text: 'Failed to fetch user messages' });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/api/admin/users`, newUser, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage({ type: 'success', text: 'User created successfully' });
      setNewUser({ email: '', name: '', password: '', is_admin: false, role: 'user' });
      fetchUsers();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to create user' });
    }
  };

  const handleUpdateUser = async (userId, updates) => {
    setLoading(true);
    try {
      if (!updates.password || updates.password.trim() === '') {
        delete updates.password;
      }
      await axios.put(`${API_URL}/api/admin/users/${userId}`, updates, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage({ type: 'success', text: 'User updated successfully' });
      setEditingUser(null);
      fetchUsers();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update user' });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    try {
      await axios.delete(`${API_URL}/api/admin/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage({ type: 'success', text: 'User deleted successfully' });
      fetchUsers();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to delete user' });
    }
  };

  const handleBulkDeleteUsers = async () => {
    if (selectedUsers.length === 0) return;
    if (!window.confirm(`Are you sure you want to delete ${selectedUsers.length} users?`)) return;
    try {
      await Promise.all(selectedUsers.map(userId => 
        axios.delete(`${API_URL}/api/admin/users/${userId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ));
      setMessage({ type: 'success', text: `${selectedUsers.length} users deleted successfully` });
      setSelectedUsers([]);
      fetchUsers();
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to delete users' });
    }
  };

  const handleSendMessageToUser = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !selectedChatUser) return;
    const messageText = chatInput.trim();
    setChatInput('');
    setLoading(true);
    try {
      const lastUserMessage = [...userMessages].reverse().find(m => m.user_message && !m.admin_response);
      if (lastUserMessage && lastUserMessage.type === 'support') {
        await axios.put(
          `${API_URL}/api/chat/admin/support/requests/${lastUserMessage.id.replace('support_', '')}`,
          {
            response: messageText,
            status: lastUserMessage.status === 'PENDING' ? 'IN_PROGRESS' : lastUserMessage.status
          },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        await axios.post(
          `${API_URL}/api/chat/admin/user/${selectedChatUser.id}/respond`,
          { message: messageText, context: { type: 'admin_response' } },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }
      fetchUserMessages(selectedChatUser.id);
      fetchUsersWithMessages();
      fetchSupportStats();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to send message' });
    } finally {
      setLoading(false);
    }
  };

  const exportUsers = () => {
    const csv = [
      ['ID', 'Name', 'Email', 'Role', 'Status', 'Created At', 'Last Login'].join(','),
      ...filteredUsers.map(u => [
        u.id,
        u.name || '',
        u.email,
        u.is_admin ? 'Admin' : u.role,
        u.is_active ? 'Active' : 'Inactive',
        u.created_at || '',
        u.last_login || ''
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `users_export_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportIncidents = () => {
    const csv = [
      ['Incident ID', 'Severity', 'Status', 'Threat Type', 'Source IP', 'Detected At'].join(','),
      ...filteredIncidents.map(i => [
        i.incident_id,
        i.severity,
        i.status,
        i.threat_type || 'N/A',
        i.source_ip || 'N/A',
        i.detected_at
      ].join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `incidents_export_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Filtered data
  const filteredUsers = useMemo(() => {
    return users.filter(user => {
      const matchesSearch = !userSearch || 
        user.name?.toLowerCase().includes(userSearch.toLowerCase()) ||
        user.email?.toLowerCase().includes(userSearch.toLowerCase());
      const matchesRole = userRoleFilter === 'ALL' || 
        (userRoleFilter === 'ADMIN' && user.is_admin) ||
        (userRoleFilter === 'USER' && !user.is_admin);
      return matchesSearch && matchesRole;
    });
  }, [users, userSearch, userRoleFilter]);

  const filteredIncidents = useMemo(() => {
    return incidents.filter(incident => {
      const matchesSearch = !incidentSearch ||
        incident.incident_id?.toLowerCase().includes(incidentSearch.toLowerCase()) ||
        incident.threat_type?.toLowerCase().includes(incidentSearch.toLowerCase()) ||
        incident.source_ip?.toLowerCase().includes(incidentSearch.toLowerCase());
      const matchesSeverity = incidentSeverityFilter === 'ALL' ||
        incident.severity?.toLowerCase() === incidentSeverityFilter.toLowerCase();
      return matchesSearch && matchesSeverity;
    });
  }, [incidents, incidentSearch, incidentSeverityFilter]);

  // Chart data
  const userRoleData = useMemo(() => {
    if (!userAnalytics) return [];
    return Object.entries(userAnalytics.users_by_role || {}).map(([role, count]) => ({
      name: role,
      value: count
    }));
  }, [userAnalytics]);

  const incidentSeverityData = useMemo(() => {
    const severityCounts = incidents.reduce((acc, inc) => {
      const sev = inc.severity?.toLowerCase() || 'unknown';
      acc[sev] = (acc[sev] || 0) + 1;
      return acc;
    }, {});
    return Object.entries(severityCounts).map(([severity, count]) => ({
      name: severity.toUpperCase(),
      value: count
    }));
  }, [incidents]);

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];

  return (
    <div className="admin-dashboard-modern">
      <ChatAssistant isAdmin={true} />
      <div className="admin-container-modern">
        {/* Header */}
        <div className="admin-header-modern">
          <div>
            <h1 className="admin-title-modern">
              <span className="admin-icon-modern">🔐</span>
              <span>Admin Dashboard</span>
            </h1>
            <p className="admin-subtitle-modern">Comprehensive system management and monitoring</p>
          </div>
          <div className="admin-controls-modern">
            <label className="auto-refresh-toggle">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              <span>Auto-refresh</span>
            </label>
            {autoRefresh && (
              <select
                className="refresh-interval-select"
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
              >
                <option value={10}>10s</option>
                <option value={30}>30s</option>
                <option value={60}>1m</option>
                <option value={300}>5m</option>
              </select>
            )}
          </div>
        </div>

        {message.text && (
          <div className={`message-modern message-${message.type}`}>
            <span>{message.text}</span>
            <button onClick={() => setMessage({ type: '', text: '' })} className="message-close">×</button>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="admin-tabs-modern">
          <button
            className={`admin-tab-modern ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <span className="tab-icon">📊</span>
            <span>Overview</span>
          </button>
          <button
            className={`admin-tab-modern ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            <span className="tab-icon">👥</span>
            <span>Users</span>
            {users.length > 0 && <span className="tab-badge">{users.length}</span>}
          </button>
          <button
            className={`admin-tab-modern ${activeTab === 'incidents' ? 'active' : ''}`}
            onClick={() => setActiveTab('incidents')}
          >
            <span className="tab-icon">🚨</span>
            <span>Incidents</span>
            {incidents.length > 0 && <span className="tab-badge">{incidents.length}</span>}
          </button>
          <button
            className={`admin-tab-modern ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <span className="tab-icon">📈</span>
            <span>Analytics</span>
          </button>
          <button
            className={`admin-tab-modern ${activeTab === 'support' ? 'active' : ''}`}
            onClick={() => setActiveTab('support')}
          >
            <span className="tab-icon">💬</span>
            <span>Support</span>
            {supportStats && supportStats.pending > 0 && (
              <span className="tab-badge urgent">{supportStats.pending}</span>
            )}
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="admin-content-modern">
            {/* Key Metrics */}
            <div className="metrics-grid-modern">
              <div className="metric-card-modern">
                <div className="metric-icon">👥</div>
                <div className="metric-content">
                  <h3>Total Users</h3>
                  <p className="metric-value">{stats.total_users}</p>
                  <p className="metric-detail">Active: {stats.active_users}</p>
                </div>
              </div>
              <div className="metric-card-modern">
                <div className="metric-icon">🔐</div>
                <div className="metric-content">
                  <h3>Admin Users</h3>
                  <p className="metric-value">{stats.admin_users}</p>
                </div>
              </div>
              <div className="metric-card-modern">
                <div className="metric-icon">🚨</div>
                <div className="metric-content">
                  <h3>Total Incidents</h3>
                  <p className="metric-value">{stats.total_incidents}</p>
                  <p className="metric-detail">Open: {stats.open_incidents}</p>
                </div>
              </div>
              <div className="metric-card-modern">
                <div className="metric-icon">✅</div>
                <div className="metric-content">
                  <h3>Resolved</h3>
                  <p className="metric-value">{stats.resolved_incidents}</p>
                  <p className="metric-detail">Resolved: {((stats.resolved_incidents / stats.total_incidents) * 100 || 0).toFixed(1)}%</p>
                </div>
              </div>
            </div>

            {/* Quick Stats Charts */}
            {userRoleData.length > 0 && (
              <div className="charts-row-modern">
                <div className="modern-card">
                  <div className="modern-card-header">
                    <h3 className="modern-card-title">User Distribution</h3>
                  </div>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={userRoleData}
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        innerRadius={50}
                        dataKey="value"
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      >
                        {userRoleData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {incidentSeverityData.length > 0 && (
                  <div className="modern-card">
                    <div className="modern-card-header">
                      <h3 className="modern-card-title">Incident Severity</h3>
                    </div>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={incidentSeverityData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#667eea" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            )}

            {/* KPI Performance Metrics Section */}
            <div className="kpi-section">
              <h2 className="section-title-modern">📊 Performance & Efficiency KPIs</h2>
              
              {/* MTTD/MTTR Trends */}
              {mttdMttrTrends && (
                <div className="modern-card">
                  <div className="modern-card-header">
                    <h3 className="modern-card-title">MTTD & MTTR Trends (30 Days)</h3>
                    <div className="kpi-summary">
                      <span>Avg MTTD: {mttdMttrTrends.average_mttd_hours}h</span>
                      <span>Avg MTTR: {mttdMttrTrends.average_mttr_hours}h</span>
                    </div>
                  </div>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={mttdMttrTrends.trends}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={(v) => format(new Date(v), 'MM/dd')} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="mttd_hours" stroke="#667eea" name="MTTD (hours)" />
                      <Line type="monotone" dataKey="mttr_hours" stroke="#ff4757" name="MTTR (hours)" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* False Positive Rate & Detection Accuracy */}
              <div className="kpi-metrics-row">
                {falsePositiveRate && (
                  <div className="modern-card kpi-card">
                    <div className="modern-card-header">
                      <h3 className="modern-card-title">False Positive Rate</h3>
                    </div>
                    <div className="kpi-gauge">
                      <div className="gauge-value">{falsePositiveRate.false_positive_rate.toFixed(2)}%</div>
                      <div className="gauge-bar">
                        <div 
                          className={`gauge-fill ${falsePositiveRate.meets_target ? 'success' : 'warning'}`}
                          style={{ width: `${Math.min(falsePositiveRate.false_positive_rate, 10)}%` }}
                        ></div>
                      </div>
                      <div className="gauge-label">
                        Target: &lt;5% {falsePositiveRate.meets_target ? '✅' : '⚠️'}
                      </div>
                      <div className="kpi-details">
                        <p>False Positives: {falsePositiveRate.false_positives}</p>
                        <p>True Positives: {falsePositiveRate.true_positives}</p>
                      </div>
                    </div>
                  </div>
                )}

                {detectionAccuracy && (
                  <div className="modern-card kpi-card">
                    <div className="modern-card-header">
                      <h3 className="modern-card-title">Detection Accuracy</h3>
                    </div>
                    <div className="kpi-gauge">
                      <div className="gauge-value">{detectionAccuracy.f1_score.toFixed(2)}%</div>
                      <div className="gauge-bar">
                        <div 
                          className={`gauge-fill ${detectionAccuracy.meets_target ? 'success' : 'warning'}`}
                          style={{ width: `${detectionAccuracy.f1_score}%` }}
                        ></div>
                      </div>
                      <div className="gauge-label">
                        F1 Score (Target: 90%+) {detectionAccuracy.meets_target ? '✅' : '⚠️'}
                      </div>
                      <div className="kpi-details">
                        <p>Precision: {detectionAccuracy.precision}%</p>
                        <p>Recall: {detectionAccuracy.recall}%</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Incident Volume by Category */}
              {incidentVolumeByCategory && (
                <div className="modern-card">
                  <div className="modern-card-header">
                    <h3 className="modern-card-title">Incident Volume by Category (30 Days)</h3>
                    <div className="kpi-summary">Total: {incidentVolumeByCategory.total_incidents} incidents</div>
                  </div>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={incidentVolumeByCategory.categories}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#667eea" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}

              {/* System Health & Compliance */}
              <div className="kpi-metrics-row">
                {serviceHealth && (
                  <div className="modern-card">
                    <div className="modern-card-header">
                      <h3 className="modern-card-title">Service Health Status</h3>
                      <span className={`status-badge status-${serviceHealth.overall_status.toLowerCase()}`}>
                        {serviceHealth.overall_status}
                      </span>
                    </div>
                    <div className="service-health-list">
                      {Object.entries(serviceHealth.services).map(([name, status]) => (
                        <div key={name} className="service-item">
                          <span className="service-name">{name.replace('_', ' ').toUpperCase()}</span>
                          <span className={`service-status status-${status.status.toLowerCase()}`}>
                            {status.status}
                          </span>
                          {status.response_time_ms && (
                            <span className="service-time">{status.response_time_ms.toFixed(0)}ms</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {complianceReadiness && (
                  <div className="modern-card">
                    <div className="modern-card-header">
                      <h3 className="modern-card-title">Compliance Readiness</h3>
                      <span className="compliance-framework">{complianceReadiness.framework}</span>
                    </div>
                    <div className="compliance-score">
                      <div className="score-circle">
                        <div className="score-value">{complianceReadiness.readiness_score.toFixed(0)}%</div>
                        <div className={`score-status ${complianceReadiness.status === 'COMPLIANT' ? 'success' : 'warning'}`}>
                          {complianceReadiness.status}
                        </div>
                      </div>
                      <div className="compliance-details">
                        <p>Resolution Rate: {complianceReadiness.resolution_rate}%</p>
                        <p>Critical Response: {complianceReadiness.critical_response_rate}%</p>
                        <p>Total Incidents (90d): {complianceReadiness.total_incidents_90d}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Log Ingestion & Resource Usage */}
              <div className="kpi-metrics-row">
                {logIngestionStatus && (
                  <div className="modern-card">
                    <div className="modern-card-header">
                      <h3 className="modern-card-title">Log Ingestion Status</h3>
                      <span className={`status-badge status-${logIngestionStatus.status.toLowerCase()}`}>
                        {logIngestionStatus.status}
                      </span>
                    </div>
                    <div className="ingestion-metrics">
                      <div className="metric-item">
                        <span className="metric-label">Target Throughput</span>
                        <span className="metric-value">{logIngestionStatus.target_throughput.toLocaleString()}/sec</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Estimated Throughput</span>
                        <span className="metric-value">{logIngestionStatus.estimated_throughput.toLocaleString()}/sec</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Incidents (Last Hour)</span>
                        <span className="metric-value">{logIngestionStatus.incidents_last_hour}</span>
                      </div>
                    </div>
                  </div>
                )}

                {resourceUsage && (
                  <div className="modern-card">
                    <div className="modern-card-header">
                      <h3 className="modern-card-title">AI/ML Resource Usage</h3>
                    </div>
                    <div className="resource-metrics">
                      <div className="metric-item">
                        <span className="metric-label">CPU Usage</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{ width: `${resourceUsage.cpu_usage_percent}%` }}
                          ></div>
                        </div>
                        <span className="metric-value">{resourceUsage.cpu_usage_percent}%</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">Memory Usage</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill" 
                            style={{ width: `${resourceUsage.memory_usage_percent}%` }}
                          ></div>
                        </div>
                        <span className="metric-value">{resourceUsage.memory_usage_percent}%</span>
                      </div>
                      <div className="metric-item">
                        <span className="metric-label">ML Service Memory</span>
                        <span className="metric-value">{resourceUsage.ml_service_memory_mb} MB</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="admin-content-modern">
            {/* Quick Actions */}
            <div className="quick-actions-modern">
              <button className="modern-btn" onClick={() => document.getElementById('create-user-form')?.scrollIntoView({ behavior: 'smooth' })}>
                ➕ Create User
              </button>
              {selectedUsers.length > 0 && (
                <button className="modern-btn modern-btn-danger" onClick={handleBulkDeleteUsers}>
                  🗑️ Delete Selected ({selectedUsers.length})
                </button>
              )}
              <button className="modern-btn modern-btn-secondary" onClick={exportUsers}>
                📥 Export CSV
              </button>
            </div>

            {/* Search and Filters */}
            <div className="modern-card">
              <div className="filters-row-modern">
                <div className="filter-group-modern">
                  <label>Search Users</label>
                  <input
                    type="text"
                    className="modern-input"
                    placeholder="Search by name or email..."
                    value={userSearch}
                    onChange={(e) => setUserSearch(e.target.value)}
                  />
                </div>
                <div className="filter-group-modern">
                  <label>Filter by Role</label>
                  <select
                    className="modern-select"
                    value={userRoleFilter}
                    onChange={(e) => setUserRoleFilter(e.target.value)}
                  >
                    <option value="ALL">All Roles</option>
                    <option value="ADMIN">Admin</option>
                    <option value="USER">User</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Create User Form */}
            <div className="modern-card" id="create-user-form">
              <div className="modern-card-header">
                <h3 className="modern-card-title">Create New User</h3>
              </div>
              <form onSubmit={handleCreateUser} className="form-modern">
                <div className="form-row-modern">
                  <div className="form-group-modern">
                    <label>Email</label>
                    <input
                      type="email"
                      className="modern-input"
                      value={newUser.email}
                      onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group-modern">
                    <label>Name</label>
                    <input
                      type="text"
                      className="modern-input"
                      value={newUser.name}
                      onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="form-group-modern">
                    <label>Password</label>
                    <input
                      type="password"
                      className="modern-input"
                      value={newUser.password}
                      onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                      required
                      minLength={8}
                    />
                  </div>
                </div>
                <div className="form-group-modern">
                  <label className="checkbox-label-modern">
                    <input
                      type="checkbox"
                      checked={newUser.is_admin}
                      onChange={(e) => setNewUser({ ...newUser, is_admin: e.target.checked, role: e.target.checked ? 'admin' : 'user' })}
                    />
                    <span>Admin User</span>
                  </label>
                </div>
                <button type="submit" className="modern-btn">Create User</button>
              </form>
            </div>

            {/* Users Table */}
            <div className="modern-card">
              <div className="modern-card-header">
                <h3 className="modern-card-title">All Users ({filteredUsers.length})</h3>
              </div>
              {loading ? (
                <div className="modern-loading">
                  <div className="modern-spinner"></div>
                  <p>Loading users...</p>
                </div>
              ) : (
                <div className="table-wrapper-modern">
                  <table className="modern-table">
                    <thead>
                      <tr>
                        <th>
                          <input
                            type="checkbox"
                            checked={selectedUsers.length === filteredUsers.length && filteredUsers.length > 0}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedUsers(filteredUsers.map(u => u.id));
                              } else {
                                setSelectedUsers([]);
                              }
                            }}
                          />
                        </th>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Created</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredUsers.map((user) => (
                        <tr key={user.id}>
                          <td>
                            <input
                              type="checkbox"
                              checked={selectedUsers.includes(user.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedUsers([...selectedUsers, user.id]);
                                } else {
                                  setSelectedUsers(selectedUsers.filter(id => id !== user.id));
                                }
                              }}
                            />
                          </td>
                          <td>{user.id}</td>
                          <td>{user.name}</td>
                          <td>{user.email}</td>
                          <td>
                            <span className={`status-badge-modern ${user.is_admin ? 'status-investigating' : 'status-resolved'}`}>
                              {user.is_admin ? 'Admin' : user.role}
                            </span>
                          </td>
                          <td>
                            <span className={`status-badge-modern ${user.is_active ? 'status-resolved' : 'status-open'}`}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td>{user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</td>
                          <td>
                            <div className="action-buttons-modern">
                              <button
                                onClick={() => {
                                  axios.get(`${API_URL}/api/admin/users/${user.id}`, {
                                    headers: { Authorization: `Bearer ${token}` }
                                  }).then(response => {
                                    setEditingUser({
                                      ...response.data,
                                      originalPassword: response.data.password || '',
                                      password: response.data.password || ''
                                    });
                                  }).catch(err => {
                                    setEditingUser({ ...user, originalPassword: '', password: '' });
                                  });
                                }}
                                className="modern-btn modern-btn-sm modern-btn-secondary"
                              >
                                ✏️ Edit
                              </button>
                              <button
                                onClick={() => handleDeleteUser(user.id)}
                                className="modern-btn modern-btn-sm modern-btn-danger"
                              >
                                🗑️ Delete
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Edit User Modal */}
            {editingUser && (
              <div className="modal-overlay-modern" onClick={() => setEditingUser(null)}>
                <div className="modal-modern" onClick={(e) => e.stopPropagation()}>
                  <div className="modal-header-modern">
                    <h3>Edit User: {editingUser.name || editingUser.email}</h3>
                    <button onClick={() => setEditingUser(null)} className="modal-close">×</button>
                  </div>
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      const updateData = {
                        name: editingUser.name,
                        email: editingUser.email,
                        is_active: editingUser.is_active,
                        is_admin: editingUser.is_admin,
                        role: editingUser.role
                      };
                      if (editingUser.password && editingUser.password.trim() && editingUser.password !== editingUser.originalPassword) {
                        if (editingUser.password.length < 8) {
                          setMessage({ type: 'error', text: 'Password must be at least 8 characters' });
                          return;
                        }
                        updateData.password = editingUser.password;
                      }
                      handleUpdateUser(editingUser.id, updateData);
                    }}
                    className="form-modern"
                  >
                    <div className="form-group-modern">
                      <label>Name</label>
                      <input
                        type="text"
                        className="modern-input"
                        value={editingUser.name || ''}
                        onChange={(e) => setEditingUser({ ...editingUser, name: e.target.value })}
                      />
                    </div>
                    <div className="form-group-modern">
                      <label>Email</label>
                      <input
                        type="email"
                        className="modern-input"
                        value={editingUser.email || ''}
                        onChange={(e) => setEditingUser({ ...editingUser, email: e.target.value })}
                      />
                    </div>
                    <div className="form-group-modern">
                      <label>Current Password</label>
                      <input
                        type="text"
                        className="modern-input"
                        value={editingUser.originalPassword || editingUser.password || 'No password set'}
                        readOnly
                        style={{ fontFamily: 'monospace', background: 'rgba(102, 126, 234, 0.1)' }}
                      />
                    </div>
                    <div className="form-group-modern">
                      <label>New Password (Optional)</label>
                      <input
                        type="password"
                        className="modern-input"
                        value={editingUser.password || ''}
                        onChange={(e) => setEditingUser({ ...editingUser, password: e.target.value })}
                        minLength={8}
                        placeholder="Leave empty to keep current"
                      />
                    </div>
                    <div className="form-group-modern">
                      <label className="checkbox-label-modern">
                        <input
                          type="checkbox"
                          checked={editingUser.is_active}
                          onChange={(e) => setEditingUser({ ...editingUser, is_active: e.target.checked })}
                        />
                        <span>Active</span>
                      </label>
                    </div>
                    <div className="form-group-modern">
                      <label className="checkbox-label-modern">
                        <input
                          type="checkbox"
                          checked={editingUser.is_admin}
                          onChange={(e) => setEditingUser({ ...editingUser, is_admin: e.target.checked, role: e.target.checked ? 'admin' : 'user' })}
                        />
                        <span>Admin</span>
                      </label>
                    </div>
                    <div className="form-actions-modern">
                      <button type="submit" className="modern-btn">Save Changes</button>
                      <button type="button" onClick={() => setEditingUser(null)} className="modern-btn modern-btn-secondary">Cancel</button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Incidents Tab */}
        {activeTab === 'incidents' && (
          <div className="admin-content-modern">
            <div className="quick-actions-modern">
              <button className="modern-btn modern-btn-secondary" onClick={exportIncidents}>
                📥 Export CSV
              </button>
            </div>

            <div className="modern-card">
              <div className="filters-row-modern">
                <div className="filter-group-modern">
                  <label>Search Incidents</label>
                  <input
                    type="text"
                    className="modern-input"
                    placeholder="Search by ID, threat type, or IP..."
                    value={incidentSearch}
                    onChange={(e) => setIncidentSearch(e.target.value)}
                  />
                </div>
                <div className="filter-group-modern">
                  <label>Filter by Severity</label>
                  <select
                    className="modern-select"
                    value={incidentSeverityFilter}
                    onChange={(e) => setIncidentSeverityFilter(e.target.value)}
                  >
                    <option value="ALL">All Severities</option>
                    <option value="CRITICAL">Critical</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="modern-card">
              <div className="modern-card-header">
                <h3 className="modern-card-title">All Incidents ({filteredIncidents.length})</h3>
              </div>
              {loading ? (
                <div className="modern-loading">
                  <div className="modern-spinner"></div>
                  <p>Loading incidents...</p>
                </div>
              ) : (
                <div className="table-wrapper-modern">
                  <table className="modern-table">
                    <thead>
                      <tr>
                        <th>Incident ID</th>
                        <th>Severity</th>
                        <th>Status</th>
                        <th>Threat Type</th>
                        <th>Source IP</th>
                        <th>Detected At</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredIncidents.map((incident) => (
                        <tr key={incident.incident_id}>
                          <td><code>{incident.incident_id.slice(0, 8)}</code></td>
                          <td>
                            <span className={`severity-badge-modern severity-${incident.severity?.toLowerCase()}`}>
                              {incident.severity}
                            </span>
                          </td>
                          <td>
                            <span className={`status-badge-modern status-${incident.status?.toLowerCase()}`}>
                              {incident.status}
                            </span>
                          </td>
                          <td>{incident.threat_type || 'N/A'}</td>
                          <td><code>{incident.source_ip || 'N/A'}</code></td>
                          <td>{new Date(incident.detected_at).toLocaleString()}</td>
                          <td>
                            <select
                              className="modern-select modern-select-sm"
                              value={incident.status}
                              onChange={(e) => {
                                axios.patch(`${API_URL}/api/incidents/${incident.incident_id}/status?status=${e.target.value}`, {}, {
                                  headers: { Authorization: `Bearer ${token}` }
                                }).then(() => {
                                  setMessage({ type: 'success', text: 'Incident status updated' });
                                  fetchIncidents();
                                }).catch(err => {
                                  setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to update incident' });
                                });
                              }}
                            >
                              <option value="OPEN">Open</option>
                              <option value="IN_PROGRESS">In Progress</option>
                              <option value="RESOLVED">Resolved</option>
                              <option value="CLOSED">Closed</option>
                            </select>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="admin-content-modern">
            {userAnalytics && (
              <div className="modern-card">
                <div className="modern-card-header">
                  <h3 className="modern-card-title">User Analytics</h3>
                </div>
                <div className="analytics-grid-modern">
                  <div className="analytics-item-modern">
                    <h4>Users by Role</h4>
                    <ul>
                      {Object.entries(userAnalytics.users_by_role || {}).map(([role, count]) => (
                        <li key={role}>
                          <strong>{role}:</strong> {count}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="analytics-item-modern">
                    <h4>User Status</h4>
                    <p>Active: <strong>{userAnalytics.active_users}</strong></p>
                    <p>Inactive: <strong>{userAnalytics.inactive_users}</strong></p>
                  </div>
                  <div className="analytics-item-modern">
                    <h4>New Users</h4>
                    <p>Last 7 days: <strong>{userAnalytics.new_users_7d}</strong></p>
                    <p>Last 30 days: <strong>{userAnalytics.new_users_30d}</strong></p>
                  </div>
                  <div className="analytics-item-modern">
                    <h4>Recent Activity</h4>
                    <p>Logins (24h): <strong>{userAnalytics.recent_logins_24h}</strong></p>
                    <p>Total Activities: <strong>{userAnalytics.total_activities}</strong></p>
                  </div>
                </div>
              </div>
            )}

            {activityAnalytics && (
              <div className="modern-card">
                <div className="modern-card-header">
                  <h3 className="modern-card-title">Activity Analytics (Last {activityAnalytics.period_days} days)</h3>
                </div>
                <div className="table-wrapper-modern">
                  <table className="modern-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Activity Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {activityAnalytics.top_active_users?.slice(0, 10).map((user, idx) => (
                        <tr key={idx}>
                          <td>{user.name}</td>
                          <td>{user.email}</td>
                          <td>{user.activity_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Support Tab - Keep existing implementation but with modern styling */}
        {activeTab === 'support' && (
          <div className="admin-content-modern">
            {supportStats && (
              <div className="metrics-grid-modern">
                <div className="metric-card-modern">
                  <div className="metric-icon">📋</div>
                  <div className="metric-content">
                    <h3>Total Requests</h3>
                    <p className="metric-value">{supportStats.total || 0}</p>
                  </div>
                </div>
                <div className="metric-card-modern">
                  <div className="metric-icon">⏳</div>
                  <div className="metric-content">
                    <h3>Pending</h3>
                    <p className="metric-value" style={{ color: '#ffc107' }}>{supportStats.pending || 0}</p>
                  </div>
                </div>
                <div className="metric-card-modern">
                  <div className="metric-icon">🔄</div>
                  <div className="metric-content">
                    <h3>In Progress</h3>
                    <p className="metric-value" style={{ color: '#667eea' }}>{supportStats.in_progress || 0}</p>
                  </div>
                </div>
                <div className="metric-card-modern">
                  <div className="metric-icon">✅</div>
                  <div className="metric-content">
                    <h3>Resolved</h3>
                    <p className="metric-value" style={{ color: '#2ed573' }}>{supportStats.resolved || 0}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Telegram-like Chat Interface - Keep existing but with modern styling */}
            <div className="modern-card">
              <div className="modern-card-header">
                <h3 className="modern-card-title">💬 User Chat Support</h3>
              </div>
              <div className="telegram-chat-container">
                <div className="chat-users-sidebar">
                  <div className="sidebar-header">
                    <h3>Users</h3>
                    <input
                      type="text"
                      placeholder="Search users..."
                      className="user-search-input"
                      onChange={(e) => {
                        const search = e.target.value.toLowerCase();
                        if (search) {
                          const filtered = usersWithMessages.filter(u => 
                            u.name?.toLowerCase().includes(search) || 
                            u.email?.toLowerCase().includes(search)
                          );
                          setUsersWithMessages(filtered);
                        } else {
                          fetchUsersWithMessages();
                        }
                      }}
                    />
                  </div>
                  <div className="users-list">
                    {usersWithMessages.length === 0 ? (
                      <div className="no-users-message">
                        <p>No users with messages yet</p>
                      </div>
                    ) : (
                      usersWithMessages.map((user) => (
                        <div
                          key={user.id}
                          className={`user-chat-item ${selectedChatUser?.id === user.id ? 'active' : ''} ${user.unreadCount > 0 ? 'has-unread' : ''}`}
                          onClick={() => {
                            setUserMessages([]);
                            setChatInput('');
                            setSelectedChatUser(user);
                          }}
                        >
                          <div className="user-avatar">
                            {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
                          </div>
                          <div className="user-info">
                            <div className="user-name-row">
                              <strong>{user.name || user.email}</strong>
                              {user.lastMessageTime && (
                                <span className="message-time-small">
                                  {new Date(user.lastMessageTime).toLocaleDateString()}
                                </span>
                              )}
                            </div>
                            <p className="user-last-message">{user.lastMessage}</p>
                          </div>
                          {user.unreadCount > 0 && (
                            <div className="unread-badge">{user.unreadCount}</div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="chat-messages-panel">
                  {selectedChatUser ? (
                    <>
                      <div className="chat-header-panel">
                        <div className="chat-user-header">
                          <div className="chat-user-avatar-large">
                            {selectedChatUser.name ? selectedChatUser.name.charAt(0).toUpperCase() : selectedChatUser.email.charAt(0).toUpperCase()}
                          </div>
                          <div>
                            <h3>{selectedChatUser.name || selectedChatUser.email}</h3>
                            <p className="user-status">
                              {selectedChatUser.is_active ? '🟢 Active' : '🔴 Inactive'}
                              {selectedChatUser.unreadCount > 0 && (
                                <span className="unread-indicator"> • {selectedChatUser.unreadCount} unread</span>
                              )}
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="chat-messages-container">
                        {loading && userMessages.length === 0 ? (
                          <div className="no-messages">
                            <p>Loading messages...</p>
                          </div>
                        ) : userMessages.length === 0 ? (
                          <div className="no-messages">
                            <p>No messages yet</p>
                          </div>
                        ) : (
                          userMessages.map((msg, idx) => (
                            <div key={msg.id || idx} className="message-thread">
                              {msg.user_message && (
                                <div className="message-bubble user-bubble">
                                  <div className="message-text">{msg.user_message}</div>
                                  <div className="message-meta">
                                    <span className="message-type-badge">{msg.type === 'support' ? '📩 Support' : '💬 Chat'}</span>
                                    <span className="message-timestamp">
                                      {new Date(msg.timestamp).toLocaleString()}
                                    </span>
                                  </div>
                                </div>
                              )}
                              {msg.admin_response ? (
                                <div className="message-bubble admin-bubble">
                                  <div className="message-text">{msg.admin_response}</div>
                                  <div className="message-meta">
                                    <span className="message-timestamp">
                                      {new Date(msg.timestamp).toLocaleString()}
                                    </span>
                                  </div>
                                </div>
                              ) : (
                                <div className="pending-response-indicator">
                                  <span>⏳ Waiting for your response...</span>
                                </div>
                              )}
                            </div>
                          ))
                        )}
                        <div ref={(el) => el?.scrollIntoView({ behavior: 'smooth' })} />
                      </div>

                      <form onSubmit={handleSendMessageToUser} className="chat-input-panel">
                        <input
                          type="text"
                          value={chatInput}
                          onChange={(e) => setChatInput(e.target.value)}
                          placeholder={`Type a message to ${selectedChatUser.name || selectedChatUser.email}...`}
                          disabled={loading}
                          className="chat-input-field"
                        />
                        <button
                          type="submit"
                          disabled={loading || !chatInput.trim()}
                          className="chat-send-btn"
                        >
                          {loading ? '⏳' : '📤'}
                        </button>
                      </form>
                    </>
                  ) : (
                    <div className="no-chat-selected">
                      <div className="empty-chat-icon">💬</div>
                      <h3>Select a user to start chatting</h3>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;
