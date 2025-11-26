import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/modern-theme.css';
import './Login.css';

const API_URL = process.env.REACT_APP_API_URL || '';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [registerData, setRegisterData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Validate input
      if (!email || !password) {
        setError('Please enter both email and password');
        setLoading(false);
        return;
      }

      // Use URLSearchParams for form-urlencoded format (OAuth2 standard)
      const params = new URLSearchParams();
      params.append('username', email.trim().toLowerCase());
      params.append('password', password);

      // Make login request - use relative path through nginx proxy
      const loginUrl = `/api/auth/login`;
      console.log('🔐 Attempting login to:', loginUrl);
      
      const response = await axios.post(
        loginUrl,
        params.toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          timeout: 10000, // 10 second timeout
        }
      );

      // Check if response is successful
      if (response.status === 200 && response.data && response.data.access_token) {
        // Store token and user info
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        console.log('✅ Login successful, redirecting...');
        
        // Redirect to dashboard
        navigate('/');
        // Small delay before reload to ensure navigation happens
        setTimeout(() => {
          window.location.reload();
        }, 100);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      console.error('❌ Login error:', err);
      
      // Handle different error types
      if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
        setError('Connection timeout. Please check if the server is running.');
      } else if (err.response) {
        // Server responded with error
        const status = err.response.status;
        const errorDetail = err.response.data?.detail || err.response.data?.message || 'Login failed';
        
        if (status === 401) {
          setError('Incorrect email or password. Please try again.');
        } else if (status === 403) {
          setError('Your account is inactive. Please contact an administrator.');
        } else if (status === 502 || status === 503) {
          setError('Server is temporarily unavailable. Please try again in a moment.');
        } else {
          setError(errorDetail);
        }
      } else if (err.request) {
        // Request made but no response
        setError('Cannot connect to server. Please check your connection and try again.');
      } else {
        // Other error
        setError(err.message || 'Login failed. Please check your credentials.');
      }
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    if (registerData.password !== registerData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (registerData.password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      await axios.post(`/api/auth/register`, {
        email: registerData.email,
        name: registerData.name,
        password: registerData.password
      });

      // Registration successful - switch to login form
      const registeredEmail = registerData.email;
      setError('');
      setLoading(false);
      
      // Clear registration form
      setRegisterData({ name: '', email: '', password: '', confirmPassword: '' });
      
      // Switch to login form
      setShowRegister(false);
      
      // Pre-fill email in login form
      setEmail(registeredEmail);
      
      // Show success message
      setSuccessMessage('Registration successful! Please login with your credentials.');
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <div className="logo-large">🛡️</div>
          <h1>SOC Assistant</h1>
          <p>AI-Driven Security Operations Center</p>
        </div>

        {!showRegister ? (
          <form onSubmit={handleLogin} className="login-form">
            <h2>Sign In</h2>
            {error && <div className="error-message">{error}</div>}
            {successMessage && <div className="success-message">{successMessage}</div>}
            
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Enter your email"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
                disabled={loading}
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>

            <div className="login-footer">
              <button
                type="button"
                className="link-button"
                onClick={() => {
                  setShowRegister(true);
                  setError('');
                  setSuccessMessage('');
                }}
              >
                Don't have an account? Register
              </button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleRegister} className="login-form">
            <h2>Register</h2>
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                value={registerData.name}
                onChange={(e) => setRegisterData({ ...registerData, name: e.target.value })}
                required
                placeholder="Enter your full name"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={registerData.email}
                onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                required
                placeholder="Enter your email"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={registerData.password}
                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                required
                placeholder="At least 8 characters"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                value={registerData.confirmPassword}
                onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                required
                placeholder="Confirm your password"
                disabled={loading}
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Registering...' : 'Register'}
            </button>

            <div className="login-footer">
              <button
                type="button"
                className="link-button"
                onClick={() => {
                  setShowRegister(false);
                  setError('');
                  setSuccessMessage('');
                }}
              >
                Already have an account? Sign In
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default Login;

