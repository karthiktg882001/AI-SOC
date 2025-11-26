import axios from "axios";
import React, { useEffect, useState } from "react";
import "../styles/modern-theme.css";
import { getDeviceInfo } from "../utils/deviceInfo";
import "./UserProfile.css";

const API_URL = process.env.REACT_APP_API_URL || "";

function UserProfile() {
  const [user, setUser] = useState(null);
  const [version, setVersion] = useState(null);
  const [deviceInfo, setDeviceInfo] = useState(getDeviceInfo());
  const [currentIP, setCurrentIP] = useState(null);
  const [publicIP, setPublicIP] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("account");

  const [showChangePassword, setShowChangePassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [message, setMessage] = useState({ type: "", text: "" });

  useEffect(() => {
    fetchUserInfo();
    fetchDeviceIP();
    fetchPublicIP();
    fetchVersion();

    const ipInterval = setInterval(() => {
      fetchDeviceIP();
      fetchPublicIP();
    }, 5000);

    const deviceInterval = setInterval(() => {
      setDeviceInfo(getDeviceInfo());
    }, 10000);

    return () => {
      clearInterval(ipInterval);
      clearInterval(deviceInterval);
    };
  }, []);

  const fetchUserInfo = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setLoading(false);
        return;
      }
      const response = await axios.get(`${API_URL}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching user info:", err);
      setLoading(false);
    }
  };

  const fetchDeviceIP = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) return;
      const response = await axios.get(`${API_URL}/api/device/device-info`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCurrentIP(response.data);
    } catch (err) {
      console.error("Error fetching device IP:", err);
    }
  };

  const fetchPublicIP = async () => {
    const services = [
      { url: "https://api.ipify.org?format=json", key: "ip" },
      { url: "https://api.ip.sb/jsonip", key: "ip" },
      { url: "https://api.myip.com/", key: "ip" },
    ];

    for (const service of services) {
      try {
        const response = await axios.get(service.url, { timeout: 5000 });
        setPublicIP({
          ip_address: response.data[service.key] || response.data,
          source: service.url.split("/")[2],
          timestamp: new Date().toISOString(),
        });
        return;
      } catch (e) {
        continue;
      }
    }
  };

  const fetchVersion = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/system/version`);
      setVersion(response.data);
    } catch (err) {
      console.error("Error fetching version:", err);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: "error", text: "New passwords do not match" });
      return;
    }
    if (passwordData.new_password.length < 8) {
      setMessage({
        type: "error",
        text: "Password must be at least 8 characters",
      });
      return;
    }

    try {
      const token = localStorage.getItem("token");
      await axios.post(
        `${API_URL}/api/auth/change-password`,
        {
          current_password: passwordData.current_password,
          new_password: passwordData.new_password,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setMessage({ type: "success", text: "Password changed successfully" });
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
      setShowChangePassword(false);
    } catch (err) {
      setMessage({
        type: "error",
        text: err.response?.data?.detail || "Failed to change password",
      });
    }
  };

  if (loading) {
    return (
      <div className="modern-loading">
        <div className="modern-spinner"></div>
        <p>Loading profile...</p>
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
              <span className="modern-page-icon">👤</span>
              <span>User Profile</span>
            </h1>
            <p className="modern-page-subtitle">
              Manage your account and view device information
            </p>
          </div>
        </div>

        {/* Message Alert */}
        {message.text && (
          <div className={`message-modern message-${message.type}`}>
            <span>{message.text}</span>
            <button
              onClick={() => setMessage({ type: "", text: "" })}
              className="message-close"
            >
              ×
            </button>
          </div>
        )}

        {/* Tabs */}
        <div className="tabs-modern">
          <button
            className={`tab-modern ${activeTab === "account" ? "active" : ""}`}
            onClick={() => setActiveTab("account")}
          >
            <span className="tab-icon">🔐</span>
            <span>Account</span>
          </button>
          <button
            className={`tab-modern ${activeTab === "device" ? "active" : ""}`}
            onClick={() => setActiveTab("device")}
          >
            <span className="tab-icon">📱</span>
            <span>Device Info</span>
          </button>
          <button
            className={`tab-modern ${activeTab === "version" ? "active" : ""}`}
            onClick={() => setActiveTab("version")}
          >
            <span className="tab-icon">ℹ️</span>
            <span>Version</span>
          </button>
        </div>

        {/* Account Tab */}
        {activeTab === "account" && (
          <div className="modern-card">
            <div className="modern-card-header">
              <h3 className="modern-card-title">Account Information</h3>
            </div>
            {user ? (
              <div className="info-grid-modern">
                <div className="info-item-modern">
                  <span className="info-label-modern">Name</span>
                  <span className="info-value-modern">
                    {user.name || "Not set"}
                  </span>
                </div>
                <div className="info-item-modern">
                  <span className="info-label-modern">Email</span>
                  <span className="info-value-modern">{user.email}</span>
                </div>
                <div className="info-item-modern">
                  <span className="info-label-modern">Account Status</span>
                  <span
                    className={`status-badge-modern ${
                      user.is_active ? "status-resolved" : "status-open"
                    }`}
                  >
                    {user.is_active ? "✅ Active" : "❌ Inactive"}
                  </span>
                </div>
                <div className="info-item-modern">
                  <span className="info-label-modern">Email Verified</span>
                  <span
                    className={`status-badge-modern ${
                      user.email_verified
                        ? "status-resolved"
                        : "status-investigating"
                    }`}
                  >
                    {user.email_verified ? "✅ Verified" : "⚠️ Not Verified"}
                  </span>
                </div>
                {user.created_at && (
                  <div className="info-item-modern">
                    <span className="info-label-modern">Member Since</span>
                    <span className="info-value-modern">
                      {new Date(user.created_at).toLocaleDateString()}
                    </span>
                  </div>
                )}
                {user.last_login && (
                  <div className="info-item-modern">
                    <span className="info-label-modern">Last Login</span>
                    <span className="info-value-modern">
                      {new Date(user.last_login).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <p>Please log in to view account information</p>
            )}

            <div className="action-buttons-modern">
              {!showChangePassword && (
                <button
                  className="modern-btn"
                  onClick={() => setShowChangePassword(true)}
                >
                  Change Password
                </button>
              )}
            </div>

            {showChangePassword && (
              <form onSubmit={handleChangePassword} className="form-modern">
                <h4>Change Password</h4>
                <div className="form-group-modern">
                  <input
                    type="password"
                    className="modern-input"
                    placeholder="Current Password"
                    value={passwordData.current_password}
                    onChange={(e) =>
                      setPasswordData({
                        ...passwordData,
                        current_password: e.target.value,
                      })
                    }
                    required
                  />
                </div>
                <div className="form-group-modern">
                  <input
                    type="password"
                    className="modern-input"
                    placeholder="New Password (min 8 characters)"
                    value={passwordData.new_password}
                    onChange={(e) =>
                      setPasswordData({
                        ...passwordData,
                        new_password: e.target.value,
                      })
                    }
                    required
                    minLength={8}
                  />
                </div>
                <div className="form-group-modern">
                  <input
                    type="password"
                    className="modern-input"
                    placeholder="Confirm New Password"
                    value={passwordData.confirm_password}
                    onChange={(e) =>
                      setPasswordData({
                        ...passwordData,
                        confirm_password: e.target.value,
                      })
                    }
                    required
                  />
                </div>
                <div className="form-actions-modern">
                  <button type="submit" className="modern-btn">
                    Change Password
                  </button>
                  <button
                    type="button"
                    className="modern-btn modern-btn-secondary"
                    onClick={() => {
                      setShowChangePassword(false);
                      setPasswordData({
                        current_password: "",
                        new_password: "",
                        confirm_password: "",
                      });
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* Device Info Tab */}
        {activeTab === "device" && (
          <div className="modern-card">
            <div className="modern-card-header">
              <h3 className="modern-card-title">Device Information</h3>
              <div className="modern-badge">Real-time</div>
            </div>
            <div className="info-grid-modern">
              {publicIP && (
                <div className="info-item-modern highlight-modern">
                  <span className="info-label-modern">
                    🌐 Public IP Address
                  </span>
                  <div className="ip-display-modern">
                    <code className="ip-code-modern">
                      {publicIP.ip_address || "Loading..."}
                    </code>
                    <span className="info-badge-modern">Real-time</span>
                  </div>
                  {publicIP.source && (
                    <span className="info-source-modern">
                      via {publicIP.source}
                    </span>
                  )}
                </div>
              )}
              {currentIP && currentIP.ip_address && (
                <div className="info-item-modern">
                  <span className="info-label-modern">Internal Network IP</span>
                  <span className="info-value-modern">
                    {currentIP.ip_address}
                  </span>
                  <span className="info-note-modern">(Docker/Internal)</span>
                </div>
              )}
              <div className="info-item-modern">
                <span className="info-label-modern">Device Type</span>
                <span className="info-value-modern">
                  {deviceInfo.deviceType}
                </span>
              </div>
              <div className="info-item-modern">
                <span className="info-label-modern">Operating System</span>
                <span className="info-value-modern">{deviceInfo.os}</span>
              </div>
              <div className="info-item-modern">
                <span className="info-label-modern">Browser</span>
                <span className="info-value-modern">
                  {deviceInfo.browser} v{deviceInfo.browserVersion}
                </span>
              </div>
              <div className="info-item-modern">
                <span className="info-label-modern">Screen Resolution</span>
                <span className="info-value-modern">
                  {deviceInfo.screen.width} × {deviceInfo.screen.height}px
                </span>
              </div>
              {currentIP && currentIP.is_secure !== undefined && (
                <div className="info-item-modern">
                  <span className="info-label-modern">Connection Security</span>
                  <span
                    className={`status-badge-modern ${
                      currentIP.is_secure
                        ? "status-resolved"
                        : "status-investigating"
                    }`}
                  >
                    {currentIP.is_secure
                      ? "🔒 Secure (HTTPS)"
                      : "⚠️ Not Secure (HTTP)"}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Version Tab */}
        {activeTab === "version" && version && (
          <div className="modern-card">
            <div className="modern-card-header">
              <h3 className="modern-card-title">Application Version</h3>
            </div>
            <div className="info-grid-modern">
              <div className="info-item-modern">
                <span className="info-label-modern">Application Name</span>
                <span className="info-value-modern">{version.name}</span>
              </div>
              <div className="info-item-modern">
                <span className="info-label-modern">Version</span>
                <span className="info-value-modern">{version.version}</span>
              </div>
              <div className="info-item-modern">
                <span className="info-label-modern">Build Date</span>
                <span className="info-value-modern">{version.build_date}</span>
              </div>
              <div className="info-item-modern">
                <span className="info-label-modern">Description</span>
                <span className="info-value-modern">{version.description}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default UserProfile;
