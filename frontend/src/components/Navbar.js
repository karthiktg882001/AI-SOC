import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import "./Navbar.css";

function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link
          to="/"
          className="navbar-logo"
          onClick={() => setMobileMenuOpen(false)}
        >
          <span className="logo-icon">🛡️</span>
          <span className="logo-text">SOC Assistant</span>
        </Link>
        <button
          className="mobile-menu-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? "✕" : "☰"}
        </button>
        <div className={`navbar-menu ${mobileMenuOpen ? "active" : ""}`}>
          <Link
            to="/"
            className="navbar-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Dashboard
          </Link>
          <Link
            to="/incidents"
            className="navbar-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Incidents
          </Link>
          <Link
            to="/reports"
            className="navbar-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Reports
          </Link>
          <Link
            to="/profile"
            className="navbar-link"
            onClick={() => setMobileMenuOpen(false)}
          >
            Profile
          </Link>
          {user && (user.is_admin || user.role === "admin") && (
            <Link
              to="/admin"
              className="navbar-link admin-link"
              onClick={() => setMobileMenuOpen(false)}
            >
              🔐 Admin
            </Link>
          )}
          {user && (
            <div className="user-menu">
              <span className="user-name">{user.name || user.email}</span>
              <button onClick={handleLogout} className="logout-btn">
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
