import axios from "axios";
import { format } from "date-fns";
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import "../styles/modern-theme.css";
import "./IncidentDetail.css";

const API_URL = process.env.REACT_APP_API_URL || "";

function IncidentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [incident, setIncident] = useState(null);
  const [report, setReport] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [xaiExplanation, setXaiExplanation] = useState(null);

  useEffect(() => {
    fetchIncident();
    fetchReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  useEffect(() => {
    if (incident) {
      fetchXAIExplanation();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [incident]);

  const fetchIncident = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_URL}/api/incidents/${id}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      setIncident(response.data);

      // Extract AI analysis from raw_log_data if available
      let aiAnalysisData = response.data.ai_analysis;
      if (!aiAnalysisData && response.data.raw_log_data) {
        const rawData =
          typeof response.data.raw_log_data === "string"
            ? JSON.parse(response.data.raw_log_data)
            : response.data.raw_log_data;
        if (rawData && rawData.ai_analysis) {
          aiAnalysisData = rawData.ai_analysis;
        }
      }

      if (aiAnalysisData) {
        setAiAnalysis(aiAnalysisData);
      }
      setLoading(false);
    } catch (err) {
      console.error("Error fetching incident:", err);
      setError(
        err.response?.data?.detail || err.message || "Failed to load incident"
      );
      setLoading(false);
    }
  };

  const fetchReport = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(
        `${API_URL}/api/incidents/${id}/report`,
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        }
      );
      if (response.data && response.data.summary) {
        setReport(response.data);
      } else {
        setReport(null);
      }
    } catch (err) {
      // Report doesn't exist yet - this is normal
      console.log(
        "Report not found (will be generated on demand):",
        err.response?.status
      );
      setReport(null);
    }
  };

  const fetchXAIExplanation = async () => {
    if (!incident) return;
    try {
      const response = await axios.get(
        `${API_URL}/api/advanced/xai/explain/${incident.incident_id}`
      );
      setXaiExplanation(response.data.explanation);
    } catch (err) {
      console.error("Failed to fetch XAI explanation:", err);
    }
  };

  const generateReport = async () => {
    setGenerating(true);
    setError(null);
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("Not authenticated. Please log in again.");
        setGenerating(false);
        return;
      }

      console.log(`Generating report for incident: ${id}`);
      const response = await axios.post(
        `${API_URL}/api/incidents/${id}/generate-report`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      console.log("Report generated:", response.data);

      // Ensure report data is valid
      if (response.data && response.data.summary) {
        setReport(response.data);
        // Refresh incident to get updated report status
        await fetchIncident();
        await fetchReport();
      } else {
        throw new Error("Report generated but missing required fields");
      }
    } catch (err) {
      console.error("Error generating report:", err);
      const errorMessage =
        err.response?.data?.detail ||
        err.message ||
        "Failed to generate report";
      setError(errorMessage);
      console.error("Full error:", {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status,
      });
    } finally {
      setGenerating(false);
    }
  };

  const updateStatus = async (status) => {
    try {
      await axios.patch(
        `${API_URL}/api/incidents/${id}/status?status=${status}`
      );
      fetchIncident();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="modern-loading">
        <div className="modern-spinner"></div>
        <p>Loading incident details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="modern-error">
        <div className="error-icon">⚠️</div>
        <p>Error: {error}</p>
        <button className="modern-btn" onClick={() => navigate("/incidents")}>
          Back to Incidents
        </button>
      </div>
    );
  }

  if (!incident) return null;

  return (
    <div className="modern-page">
      <div className="modern-container">
        {/* Back Button */}
        <button
          onClick={() => navigate("/incidents")}
          className="back-btn-modern"
        >
          <span className="back-icon">←</span>
          <span>Back to Incidents</span>
        </button>

        {/* Header */}
        <div className="modern-page-header">
          <div>
            <h1 className="modern-page-title">
              <span className="modern-page-icon">🔍</span>
              <span>{incident.threat_type || "Unknown Threat"}</span>
            </h1>
            <div className="incident-meta-header">
              <span
                className={`severity-badge-modern severity-${incident.severity.toLowerCase()}`}
              >
                {incident.severity}
              </span>
              <span className="meta-separator">•</span>
              <span className="meta-text">
                Score: {(incident.anomaly_score * 100).toFixed(1)}%
              </span>
              <span className="meta-separator">•</span>
              <span
                className={`status-badge-modern status-${incident.status.toLowerCase()}`}
              >
                {incident.status}
              </span>
            </div>
          </div>
          <div className="incident-actions-modern">
            {incident.status === "OPEN" && (
              <button
                onClick={() => updateStatus("RESOLVED")}
                className="modern-btn"
              >
                ✅ Mark as Resolved
              </button>
            )}
            {incident.status === "RESOLVED" && (
              <button
                onClick={() => updateStatus("OPEN")}
                className="modern-btn modern-btn-secondary"
              >
                🔄 Reopen
              </button>
            )}
          </div>
        </div>

        {/* Incident Details & AI Analysis Grid */}
        <div className="detail-grid-modern">
          {/* Incident Details Card */}
          <div className="modern-card">
            <div className="modern-card-header">
              <h3 className="modern-card-title">Incident Details</h3>
              <div className="modern-badge">
                #{incident.incident_id.slice(0, 8)}
              </div>
            </div>
            <div className="detail-list-modern">
              <div className="detail-item-modern">
                <span className="detail-label-modern">Incident ID</span>
                <code className="detail-value-code">
                  {incident.incident_id}
                </code>
              </div>
              <div className="detail-item-modern">
                <span className="detail-label-modern">Source IP</span>
                <code className="detail-value-code">
                  {incident.source_ip || "N/A"}
                </code>
              </div>
              <div className="detail-item-modern">
                <span className="detail-label-modern">Destination IP</span>
                <code className="detail-value-code">
                  {incident.destination_ip || "N/A"}
                </code>
              </div>
              <div className="detail-item-modern">
                <span className="detail-label-modern">Detected At</span>
                <span className="detail-value-modern">
                  {format(
                    new Date(incident.detected_at),
                    "MMM dd, yyyy HH:mm:ss"
                  )}
                </span>
              </div>
              <div className="detail-item-modern full-width">
                <span className="detail-label-modern">Description</span>
                <p className="detail-description-modern">
                  {incident.description || "No description available"}
                </p>
              </div>
            </div>
          </div>

          {/* AI Analysis Card */}
          <div className="modern-card">
            <div className="modern-card-header">
              <h3 className="modern-card-title">🤖 AI-Generated Analysis</h3>
              <div className="modern-badge">AI Powered</div>
            </div>
            {aiAnalysis || report ? (
              <div className="ai-analysis-content">
                {aiAnalysis && aiAnalysis.threat_classification && (
                  <div className="analysis-section-modern">
                    <h4>🎯 Threat Classification</h4>
                    <div className="classification-grid-modern">
                      <div className="class-item-modern">
                        <span className="class-label-modern">Primary Type</span>
                        <span className="class-value-modern">
                          {aiAnalysis.threat_classification.primary_type}
                        </span>
                      </div>
                      <div className="class-item-modern">
                        <span className="class-label-modern">Severity</span>
                        <span
                          className={`severity-badge-modern severity-${aiAnalysis.threat_classification.severity.toLowerCase()}`}
                        >
                          {aiAnalysis.threat_classification.severity}
                        </span>
                      </div>
                      <div className="class-item-modern">
                        <span className="class-label-modern">Confidence</span>
                        <span className="class-value-modern">
                          {(
                            aiAnalysis.threat_classification.confidence * 100
                          ).toFixed(1)}
                          %
                        </span>
                      </div>
                      {aiAnalysis.threat_classification.zero_day_indicator && (
                        <div className="class-item-modern full-width">
                          <div className="zero-day-badge-modern">
                            🆕 ZERO-DAY THREAT DETECTED
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {aiAnalysis && aiAnalysis.technical_analysis && (
                  <div className="analysis-section-modern">
                    <h4>🔍 Technical Analysis</h4>
                    {aiAnalysis.technical_analysis.attack_vector && (
                      <div className="analysis-item-modern">
                        <span className="analysis-label-modern">
                          Attack Vector:
                        </span>
                        <span className="analysis-value-modern">
                          {aiAnalysis.technical_analysis.attack_vector}
                        </span>
                      </div>
                    )}
                    {aiAnalysis.technical_analysis.potential_impact && (
                      <div className="analysis-item-modern">
                        <span className="analysis-label-modern">
                          Potential Impact:
                        </span>
                        <span className="analysis-value-modern">
                          {aiAnalysis.technical_analysis.potential_impact}
                        </span>
                      </div>
                    )}
                    {aiAnalysis.technical_analysis.indicators_of_compromise &&
                      aiAnalysis.technical_analysis.indicators_of_compromise
                        .length > 0 && (
                        <div className="analysis-item-modern">
                          <span className="analysis-label-modern">
                            Indicators of Compromise (IOCs):
                          </span>
                          <div className="iocs-grid-modern">
                            {aiAnalysis.technical_analysis.indicators_of_compromise.map(
                              (ioc, idx) => (
                                <div key={idx} className="ioc-item-modern">
                                  <span
                                    className={`ioc-type-modern ${ioc.severity?.toLowerCase()}`}
                                  >
                                    {ioc.type}
                                  </span>
                                  <code className="ioc-value-modern">
                                    {ioc.value}
                                  </code>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}
                  </div>
                )}

                {/* XAI Explanation Section */}
                {xaiExplanation && (
                  <div className="analysis-section-modern">
                    <h4>🔬 Explainable AI (XAI) Analysis</h4>
                    <div className="xai-content-modern">
                      <div className="xai-summary-modern">
                        {xaiExplanation.explanation_summary}
                      </div>
                      {xaiExplanation.top_contributing_features &&
                        xaiExplanation.top_contributing_features.length > 0 && (
                          <div className="xai-features-modern">
                            <h5>Top Contributing Features:</h5>
                            <div className="features-list-modern">
                              {xaiExplanation.top_contributing_features.map(
                                (feature, idx) => (
                                  <div
                                    key={idx}
                                    className="feature-item-modern"
                                  >
                                    <span className="feature-name-modern">
                                      {feature.feature
                                        .replace(/_/g, " ")
                                        .replace(/\b\w/g, (l) =>
                                          l.toUpperCase()
                                        )}
                                    </span>
                                    <div className="feature-bar-modern">
                                      <div
                                        className={`feature-fill-modern ${
                                          feature.contribution > 0
                                            ? "positive"
                                            : "negative"
                                        }`}
                                        style={{
                                          width: `${
                                            Math.abs(feature.contribution) * 100
                                          }%`,
                                        }}
                                      ></div>
                                    </div>
                                    <span className="feature-value-modern">
                                      {feature.contribution > 0 ? "+" : ""}
                                      {feature.contribution.toFixed(3)}
                                    </span>
                                  </div>
                                )
                              )}
                            </div>
                          </div>
                        )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="no-analysis-modern">
                <div className="no-analysis-icon">🤖</div>
                <p>
                  No AI analysis available yet. Generate an AI-powered analysis
                  report.
                </p>
                <button
                  onClick={generateReport}
                  disabled={generating}
                  className="modern-btn"
                >
                  {generating ? "🔄 Generating..." : "✨ Generate AI Report"}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Report Sections - Always show if report exists, or generate if not */}
        {report ? (
          <div className="report-sections-modern">
            <div className="modern-card">
              <div className="modern-card-header">
                <h3 className="modern-card-title">📋 Summary</h3>
              </div>
              <div className="report-text-modern">
                {report.summary || "No summary available"}
              </div>
            </div>

            <div className="modern-card">
              <div className="modern-card-header">
                <h3 className="modern-card-title">📊 Detailed Analysis</h3>
              </div>
              <div className="report-text-modern">
                {report.detailed_analysis || "No detailed analysis available"}
              </div>
            </div>

            <div className="modern-card">
              <div className="modern-card-header">
                <h3 className="modern-card-title">🛡️ Mitigation Steps</h3>
              </div>
              {report.mitigation_steps && report.mitigation_steps.length > 0 ? (
                <ul className="mitigation-steps-modern">
                  {report.mitigation_steps.map((step, idx) => (
                    <li key={idx}>
                      <span className="step-number">{idx + 1}</span>
                      <span className="step-text">
                        {typeof step === "string" ? step : JSON.stringify(step)}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="report-text-modern">
                  No mitigation steps available. Generate a report to get
                  AI-generated recommendations.
                </div>
              )}
            </div>

            {report.mitigation_script && (
              <div className="modern-card">
                <div className="modern-card-header">
                  <h3 className="modern-card-title">⚙️ Mitigation Script</h3>
                </div>
                <pre className="mitigation-script-modern">
                  {report.mitigation_script}
                </pre>
              </div>
            )}
          </div>
        ) : (
          <div className="modern-card">
            <div className="modern-card-header">
              <h3 className="modern-card-title">📋 AI Analysis Report</h3>
            </div>
            <div className="no-analysis-modern">
              <div className="no-analysis-icon">📊</div>
              <p>
                No detailed analysis report available yet. Generate an
                AI-powered report to get summary, detailed analysis, and
                mitigation steps.
              </p>
              <button
                onClick={generateReport}
                disabled={generating}
                className="modern-btn"
              >
                {generating ? "🔄 Generating..." : "✨ Generate AI Report"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default IncidentDetail;
