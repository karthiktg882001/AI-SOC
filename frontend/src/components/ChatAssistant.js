import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../hooks/useAuth';
import './ChatAssistant.css';

const API_URL = process.env.REACT_APP_API_URL || '';

function ChatAssistant({ isAdmin = false }) {
  const { token, user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [showSupportRequest, setShowSupportRequest] = useState(false);
  const [supportRequests, setSupportRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [supportResponse, setSupportResponse] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      if (isAdmin) {
        loadSupportRequests();
        // Don't load regular chat history for admin - focus on user requests
      } else {
        loadChatHistory();
        loadMySupportRequests();
      }
    }
  }, [isOpen, isAdmin]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatHistory = async () => {
    try {
      const endpoint = isAdmin 
        ? `${API_URL}/api/chat/admin/chat/history`
        : `${API_URL}/api/chat/history`;
      
      const response = await axios.get(endpoint, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(response.data.reverse() || []);
    } catch (err) {
      console.error('Error loading chat history:', err);
    }
  };

  const loadMySupportRequests = async () => {
    if (isAdmin) return;
    try {
      const response = await axios.get(`${API_URL}/api/chat/support/my-requests`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSupportRequests(response.data || []);
    } catch (err) {
      console.error('Error loading support requests:', err);
    }
  };

  const loadSupportRequests = async () => {
    if (!isAdmin) return;
    try {
      const response = await axios.get(`${API_URL}/api/chat/admin/support/requests`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSupportRequests(response.data || []);
    } catch (err) {
      console.error('Error loading support requests:', err);
    }
  };

  const sendSupportRequest = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const message = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    try {
      await axios.post(
        `${API_URL}/api/chat/support/request`,
        { 
          message: message,
          subject: `Support Request from ${user?.name || user?.email}`,
          priority: 'NORMAL'
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setShowSupportRequest(false);
      loadMySupportRequests();
      alert('Support request sent! An admin will respond soon.');
    } catch (err) {
      alert('Failed to send support request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const respondToRequest = async (requestId) => {
    if (!supportResponse.trim()) return;
    
    setLoading(true);
    try {
      const currentStatus = selectedRequest.status === 'PENDING' ? 'IN_PROGRESS' : selectedRequest.status;
      await axios.put(
        `${API_URL}/api/chat/admin/support/requests/${requestId}`,
        { 
          response: supportResponse,
          status: currentStatus === 'IN_PROGRESS' ? 'RESOLVED' : currentStatus
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Refresh the selected request to show the response
      const updatedRequests = await axios.get(`${API_URL}/api/chat/admin/support/requests`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const updatedRequest = updatedRequests.data.find(r => r.id === requestId);
      if (updatedRequest) {
        setSelectedRequest(updatedRequest);
      }
      
      setSupportResponse('');
      loadSupportRequests();
      // Don't close - show the response
    } catch (err) {
      alert('Failed to send response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    // Add user message to UI immediately
    const tempUserMsg = {
      id: Date.now(),
      message: userMessage,
      response: null,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const endpoint = isAdmin
        ? `${API_URL}/api/chat/admin/chat`
        : `${API_URL}/api/chat/help`;
      
      const response = await axios.post(
        endpoint,
        { 
          message: userMessage,
          context: { type: isAdmin ? 'admin' : 'user' }
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update with response
      setMessages(prev => prev.map(msg => 
        msg.id === tempUserMsg.id 
          ? { ...msg, response: response.data.response, id: response.data.message_id }
          : msg
      ));
    } catch (err) {
      setMessages(prev => prev.map(msg => 
        msg.id === tempUserMsg.id 
          ? { ...msg, response: 'Sorry, I encountered an error. Please try again.' }
          : msg
      ));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {!isOpen && (
        <button 
          className="chat-toggle-button"
          onClick={() => setIsOpen(true)}
          title="Open Chat Assistant"
        >
          💬
        </button>
      )}

      {isOpen && (
        <div className="chat-assistant">
          <div className="chat-header">
            <h3>{isAdmin ? '🔐 Admin Chat' : '💬 Chat Assistant'}</h3>
            <div className="chat-header-actions">
              {!isAdmin && (
                <button
                  className="support-request-button"
                  onClick={() => setShowSupportRequest(!showSupportRequest)}
                  title="Request help from admin"
                >
                  📩
                </button>
              )}
              <button 
                className="chat-close-button"
                onClick={() => setIsOpen(false)}
              >
                ✕
              </button>
            </div>
          </div>
          
          {isAdmin && !selectedRequest && (
            <div className="support-requests-list">
              <h4>👥 User Support Requests</h4>
              {supportRequests.length === 0 ? (
                <p className="no-requests">No pending support requests</p>
              ) : (
                <>
                  {supportRequests.filter(r => r.status === 'PENDING' || r.status === 'IN_PROGRESS').length > 0 ? (
                    supportRequests.filter(r => r.status === 'PENDING' || r.status === 'IN_PROGRESS').map(req => (
                      <div 
                        key={req.id} 
                        className="support-request-item active"
                        onClick={() => setSelectedRequest(req)}
                      >
                        <div className="request-header">
                          <strong>{req.user_name || req.user_email}</strong>
                          <span className={`status-badge ${req.status.toLowerCase()}`}>{req.status}</span>
                        </div>
                        <p className="request-preview">{req.message.substring(0, 100)}...</p>
                        <small>{new Date(req.created_at).toLocaleString()}</small>
                      </div>
                    ))
                  ) : (
                    <p className="no-requests">No active requests</p>
                  )}
                  {supportRequests.filter(r => r.status === 'RESOLVED' || r.status === 'CLOSED').length > 0 && (
                    <div className="resolved-requests">
                      <h5>Resolved Requests</h5>
                      {supportRequests.filter(r => r.status === 'RESOLVED' || r.status === 'CLOSED').slice(0, 5).map(req => (
                        <div 
                          key={req.id} 
                          className="support-request-item resolved"
                          onClick={() => setSelectedRequest(req)}
                        >
                          <div className="request-header">
                            <strong>{req.user_name || req.user_email}</strong>
                            <span className={`status-badge ${req.status.toLowerCase()}`}>{req.status}</span>
                          </div>
                          <p className="request-preview">{req.message.substring(0, 80)}...</p>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {selectedRequest && isAdmin && (
            <div className="support-request-detail">
              <button 
                className="back-button"
                onClick={() => {
                  setSelectedRequest(null);
                  setSupportResponse('');
                  loadSupportRequests(); // Refresh list when going back
                }}
              >
                ← Back to Requests
              </button>
              <div className="request-detail">
                <div className="user-info">
                  <h4>👤 User: {selectedRequest.user_name || selectedRequest.user_email}</h4>
                  <div className="request-meta">
                    <span className="meta-item">Status: <strong>{selectedRequest.status}</strong></span>
                    <span className="meta-item">Priority: <strong>{selectedRequest.priority}</strong></span>
                    <span className="meta-item">Created: {new Date(selectedRequest.created_at).toLocaleString()}</span>
                  </div>
                </div>
                
                <div className="user-message-box">
                  <h5>📝 User's Message:</h5>
                  <p className="request-message">{selectedRequest.message}</p>
                </div>
                
                {selectedRequest.response ? (
                  <div className="admin-response-box">
                    <h5>✅ Your Response:</h5>
                    <p className="admin-response-text">{selectedRequest.response}</p>
                    <p className="response-time">Responded: {selectedRequest.responded_at ? new Date(selectedRequest.responded_at).toLocaleString() : 'N/A'}</p>
                    <button
                      onClick={() => {
                        setSupportResponse(selectedRequest.response);
                        setSelectedRequest({...selectedRequest, response: null}); // Allow editing
                      }}
                      className="edit-response-button"
                    >
                      Edit Response
                    </button>
                  </div>
                ) : (
                  <div className="response-form">
                    <h5>💬 Your Response:</h5>
                    <textarea
                      value={supportResponse}
                      onChange={(e) => setSupportResponse(e.target.value)}
                      placeholder="Type your response to help the user..."
                      rows="6"
                      className="response-textarea"
                    />
                    <div className="response-actions">
                      <button
                        onClick={() => respondToRequest(selectedRequest.id)}
                        disabled={!supportResponse.trim() || loading}
                        className="send-response-button"
                      >
                        {loading ? 'Sending...' : '✓ Send Response'}
                      </button>
                      <select
                        value={selectedRequest.status}
                        onChange={(e) => {
                          const newStatus = e.target.value;
                          axios.put(
                            `${API_URL}/api/chat/admin/support/requests/${selectedRequest.id}`,
                            { status: newStatus },
                            { headers: { Authorization: `Bearer ${token}` } }
                          ).then(() => {
                            setSelectedRequest({...selectedRequest, status: newStatus});
                            loadSupportRequests();
                          });
                        }}
                        className="status-select"
                      >
                        <option value="PENDING">Pending</option>
                        <option value="IN_PROGRESS">In Progress</option>
                        <option value="RESOLVED">Resolved</option>
                        <option value="CLOSED">Closed</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {!isAdmin && showSupportRequest && (
            <div className="support-request-form">
              <h4>Request Help from Admin</h4>
              <form onSubmit={sendSupportRequest}>
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Describe your issue or question..."
                  rows="4"
                  className="support-textarea"
                  required
                />
                <div className="support-form-actions">
                  <button type="submit" disabled={loading || !inputMessage.trim()} className="send-support-button">
                    Send Request
                  </button>
                  <button type="button" onClick={() => {
                    setShowSupportRequest(false);
                    setInputMessage('');
                  }} className="cancel-button">
                    Cancel
                  </button>
                </div>
              </form>
              {supportRequests.length > 0 && (
                <div className="my-requests">
                  <h5>My Requests</h5>
                  {supportRequests.map(req => (
                    <div key={req.id} className="my-request-item">
                      <div className="request-status">
                        <strong>{req.status}</strong>
                        {req.response && <span className="has-response">✓ Responded</span>}
                      </div>
                      <p>{req.message.substring(0, 80)}...</p>
                      {req.response && (
                        <div className="admin-response-preview">
                          <strong>Admin:</strong> {req.response.substring(0, 100)}...
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {!showSupportRequest && !selectedRequest && (
            <div className="chat-messages">
              {!isAdmin && messages.length === 0 && (
                <div className="chat-welcome">
                  <p>👋 Hello! I'm your SOC Assistant.</p>
                  <p>How can I help you today?</p>
                  <p className="user-note">Need help from an admin? Click the 📩 button to send a support request.</p>
                </div>
              )}
              
              {isAdmin && messages.length === 0 && (
                <div className="chat-welcome">
                  <p>👋 Admin Chat Assistant</p>
                  <p>View and respond to user support requests above.</p>
                  <p className="admin-note">Click on any user request to view details and respond.</p>
                </div>
              )}
            
            {messages.map((msg) => (
              <div key={msg.id || Date.now()} className="chat-message-group">
                <div className="chat-message user-message">
                  <div className="message-content">{msg.message}</div>
                  <div className="message-time">
                    {new Date(msg.created_at).toLocaleTimeString()}
                  </div>
                </div>
                
                {msg.response && (
                  <div className="chat-message assistant-message">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content">{msg.response}</div>
                    <div className="message-time">
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                )}
                
                {!msg.response && loading && (
                  <div className="chat-message assistant-message">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content typing">Thinking...</div>
                  </div>
                )}
              </div>
            ))}
              <div ref={messagesEndRef} />
            </div>
          )}

          {!showSupportRequest && !selectedRequest && (
            <form onSubmit={sendMessage} className="chat-input-form">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder={isAdmin ? "Ask about admin features (or respond to user requests above)..." : "Ask me anything..."}
                disabled={loading}
                className="chat-input"
              />
              <button 
                type="submit" 
                disabled={loading || !inputMessage.trim()}
                className="chat-send-button"
              >
                {loading ? '⏳' : '📤'}
              </button>
          </form>
          )}
        </div>
      )}
    </>
  );
}

export default ChatAssistant;

