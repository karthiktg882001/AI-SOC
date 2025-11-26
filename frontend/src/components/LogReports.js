import axios from "axios";
import React, { useState } from "react";
import "../styles/modern-theme.css";
import "./LogReports.css";

const API_URL = process.env.REACT_APP_API_URL || "";

function LogReports() {
  const [reportType, setReportType] = useState("single");
  const [singleLogData, setSingleLogData] = useState("");
  const [incidentId, setIncidentId] = useState("");
  const [report, setReport] = useState(null);
  const [allLogsReport, setAllLogsReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({
    start_date: "",
    end_date: "",
    severity: "",
    threat_type: "",
  });

  const handleGenerateSingleReport = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setReport(null);

    try {
      const token = localStorage.getItem("token");

      // If incident ID is provided, use it; otherwise use JSON log data
      if (incidentId && incidentId.trim()) {
        // Generate report from incident
        const response = await axios.post(
          `${API_URL}/api/incidents/${incidentId.trim()}/generate-report`,
          {},
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setReport(response.data);
      } else if (singleLogData && singleLogData.trim()) {
        // Legacy: Generate report from JSON log data
        let logData;
        try {
          logData = JSON.parse(singleLogData);
        } catch (err) {
          throw new Error(
            "Invalid JSON format. Please enter valid JSON or an Incident ID."
          );
        }

        const response = await axios.post(
          `${API_URL}/api/log-reports/generate`,
          {
            log_data: logData,
            include_analysis: true,
            include_recommendations: true,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setReport(response.data);
      } else {
        throw new Error(
          "Please provide either an Incident ID or JSON log data."
        );
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Failed to generate report"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAllLogsReport = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setAllLogsReport(null);

    try {
      const token = localStorage.getItem("token");
      const response = await axios.post(
        `${API_URL}/api/log-reports/generate-all`,
        {
          start_date: filters.start_date || null,
          end_date: filters.end_date || null,
          severity_filter: filters.severity || null,
          threat_type_filter: filters.threat_type || null,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setAllLogsReport(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || err.message || "Failed to generate report"
      );
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (reportData, filename) => {
    const dataStr = JSON.stringify(reportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="modern-page">
      <div className="modern-container">
        {/* Header */}
        <div className="modern-page-header">
          <div>
            <h1 className="modern-page-title">
              <span className="modern-page-icon">📊</span>
              <span>AI-Powered Log Reports</span>
            </h1>
            <p className="modern-page-subtitle">
              Generate intelligent security analysis reports
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="message-modern message-error">
            <span>{error}</span>
            <button onClick={() => setError("")} className="message-close">
              ×
            </button>
          </div>
        )}

        {/* Report Type Selector */}
        <div className="report-type-selector-modern">
          <button
            className={`type-btn-modern ${
              reportType === "single" ? "active" : ""
            }`}
            onClick={() => setReportType("single")}
          >
            <span className="type-icon">📄</span>
            <span>Single Log Report</span>
          </button>
          <button
            className={`type-btn-modern ${
              reportType === "all" ? "active" : ""
            }`}
            onClick={() => setReportType("all")}
          >
            <span className="type-icon">📚</span>
            <span>All Logs Report</span>
          </button>
        </div>

        {/* Single Log Report */}
        {reportType === "single" ? (
          <div className="modern-card">
            <div className="modern-card-header">
              <h3 className="modern-card-title">
                Generate Report for Incident
              </h3>
              <div className="modern-badge">AI Analysis</div>
            </div>
            <form onSubmit={handleGenerateSingleReport} className="form-modern">
              <div className="form-group-modern">
                <label>Incident ID</label>
                <input
                  type="text"
                  className="modern-input"
                  value={incidentId}
                  onChange={(e) => {
                    setIncidentId(e.target.value);
                    setSingleLogData(""); // Clear JSON when incident ID is entered
                  }}
                  placeholder="e.g., INC-001 or UUID"
                />
                <small className="form-hint">
                  Enter the Incident ID to generate an AI-powered analysis
                  report
                </small>
              </div>
              <div
                style={{
                  textAlign: "center",
                  margin: "20px 0",
                  color: "rgba(255,255,255,0.5)",
                }}
              >
                OR
              </div>
              <div
                className="form-group-modern"
                style={{
                  marginTop: "20px",
                  paddingTop: "20px",
                  borderTop: "1px solid rgba(255,255,255,0.1)",
                }}
              >
                <label>Log Data (JSON Format) - Legacy</label>
                <textarea
                  className="modern-textarea"
                  value={singleLogData}
                  onChange={(e) => {
                    setSingleLogData(e.target.value);
                    setIncidentId(""); // Clear incident ID when JSON is entered
                  }}
                  placeholder='{"source": "firewall", "timestamp": "2024-01-15T10:30:00Z", "logLevel": "ERROR", "message": "Port scan detected", "metadata": {"ip": "192.168.1.100"}}'
                  rows="6"
                />
                <small className="form-hint">
                  Optional: Use JSON format for direct log analysis (legacy
                  mode)
                </small>
              </div>
              <button
                type="submit"
                className="modern-btn"
                disabled={
                  loading || (!incidentId.trim() && !singleLogData.trim())
                }
              >
                {loading ? "🔄 Generating Report..." : "✨ Generate AI Report"}
              </button>
            </form>

            {report && (
              <div className="report-result-modern">
                <div className="report-header-modern">
                  <h3>Generated Report</h3>
                  <button
                    onClick={() =>
                      downloadReport(
                        report,
                        `incident-report-${
                          report.incident_id || report.log_id || "report"
                        }.json`
                      )
                    }
                    className="modern-btn modern-btn-secondary"
                  >
                    📥 Download Report
                  </button>
                </div>

                <div className="report-content-modern">
                  {/* Incident Report Format */}
                  {report.summary !== undefined ? (
                    <>
                      <div className="report-section-modern">
                        <h4>📋 Summary</h4>
                        <p className="report-text-modern">
                          {report.summary || "No summary available"}
                        </p>
                      </div>

                      <div className="report-section-modern">
                        <h4>📊 Detailed Analysis</h4>
                        <p className="report-text-modern">
                          {report.detailed_analysis ||
                            "No detailed analysis available"}
                        </p>
                      </div>

                      <div className="report-section-modern">
                        <h4>🛡️ Mitigation Steps</h4>
                        {report.mitigation_steps &&
                        report.mitigation_steps.length > 0 ? (
                          <ul className="recommendations-list">
                            {report.mitigation_steps.map((step, idx) => (
                              <li key={idx}>
                                {typeof step === "string"
                                  ? step
                                  : JSON.stringify(step)}
                              </li>
                            ))}
                          </ul>
                        ) : (
                          <p className="report-text-modern">
                            No mitigation steps available
                          </p>
                        )}
                      </div>

                      {report.mitigation_script && (
                        <div className="report-section-modern">
                          <h4>⚙️ Mitigation Script</h4>
                          <pre className="report-json">
                            {report.mitigation_script}
                          </pre>
                        </div>
                      )}
                    </>
                  ) : (
                    /* Legacy Log Report Format */
                    <>
                      {report.threat_assessment && (
                        <div className="report-section-modern">
                          <h4>🎯 Threat Assessment</h4>
                          <div className="assessment-grid">
                            <div className="assessment-item">
                              <span className="assessment-label">
                                Is Threat:
                              </span>
                              <span
                                className={`assessment-value ${
                                  report.threat_assessment.is_threat
                                    ? "threat-yes"
                                    : "threat-no"
                                }`}
                              >
                                {report.threat_assessment.is_threat
                                  ? "⚠️ Yes"
                                  : "✅ No"}
                              </span>
                            </div>
                            <div className="assessment-item">
                              <span className="assessment-label">
                                Severity:
                              </span>
                              <span
                                className={`severity-badge-modern severity-${report.threat_assessment.severity.toLowerCase()}`}
                              >
                                {report.threat_assessment.severity}
                              </span>
                            </div>
                            <div className="assessment-item">
                              <span className="assessment-label">
                                Confidence:
                              </span>
                              <span className="assessment-value">
                                {report.threat_assessment.confidence.toFixed(2)}
                                %
                              </span>
                            </div>
                          </div>
                        </div>
                      )}

                      {report.analysis_summary && (
                        <div className="report-section-modern">
                          <h4>📋 Analysis Summary</h4>
                          <p className="report-text-modern">
                            {report.analysis_summary}
                          </p>
                        </div>
                      )}

                      {report.recommendations &&
                        report.recommendations.length > 0 && (
                          <div className="report-section-modern">
                            <h4>💡 Recommendations</h4>
                            <ul className="recommendations-list">
                              {report.recommendations.map((rec, idx) => (
                                <li key={idx}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                      {report.report && (
                        <div className="report-section-modern">
                          <h4>📄 Full Report</h4>
                          <pre className="report-json">
                            {JSON.stringify(report.report, null, 2)}
                          </pre>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          /* All Logs Report */
          <div className="modern-card">
            <div className="modern-card-header">
              <h3 className="modern-card-title">
                Generate Comprehensive Report for All Logs
              </h3>
              <div className="modern-badge">Comprehensive</div>
            </div>
            <form
              onSubmit={handleGenerateAllLogsReport}
              className="form-modern"
            >
              <div className="filters-grid-modern">
                <div className="form-group-modern">
                  <label>Start Date</label>
                  <input
                    type="datetime-local"
                    className="modern-input"
                    value={filters.start_date}
                    onChange={(e) =>
                      setFilters({ ...filters, start_date: e.target.value })
                    }
                  />
                </div>
                <div className="form-group-modern">
                  <label>End Date</label>
                  <input
                    type="datetime-local"
                    className="modern-input"
                    value={filters.end_date}
                    onChange={(e) =>
                      setFilters({ ...filters, end_date: e.target.value })
                    }
                  />
                </div>
                <div className="form-group-modern">
                  <label>Severity Filter</label>
                  <select
                    className="modern-select"
                    value={filters.severity}
                    onChange={(e) =>
                      setFilters({ ...filters, severity: e.target.value })
                    }
                  >
                    <option value="">All Severities</option>
                    <option value="CRITICAL">Critical</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                </div>
                <div className="form-group-modern">
                  <label>Threat Type Filter</label>
                  <input
                    type="text"
                    className="modern-input"
                    value={filters.threat_type}
                    onChange={(e) =>
                      setFilters({ ...filters, threat_type: e.target.value })
                    }
                    placeholder="e.g., malware, brute_force"
                  />
                </div>
              </div>
              <button type="submit" className="modern-btn" disabled={loading}>
                {loading
                  ? "🔄 Generating Report..."
                  : "✨ Generate Comprehensive Report"}
              </button>
            </form>

            {allLogsReport && (
              <div className="report-result-modern">
                <div className="report-header-modern">
                  <h3>Comprehensive Report</h3>
                  <button
                    onClick={() =>
                      downloadReport(
                        allLogsReport,
                        `all-logs-report-${allLogsReport.report_id}.json`
                      )
                    }
                    className="modern-btn modern-btn-secondary"
                  >
                    📥 Download Report
                  </button>
                </div>

                <div className="report-content-modern">
                  <div className="report-section-modern">
                    <h4>📊 Executive Summary</h4>
                    <p className="report-text-modern">
                      {allLogsReport.executive_summary}
                    </p>
                  </div>

                  <div className="report-section-modern">
                    <h4>📈 Statistics</h4>
                    <div className="stats-grid-modern">
                      <div className="stat-item-modern">
                        <span className="stat-label-modern">
                          Total Incidents
                        </span>
                        <span className="stat-value-modern">
                          {allLogsReport.detailed_statistics.total_incidents}
                        </span>
                      </div>
                      <div className="stat-item-modern">
                        <span className="stat-label-modern">Critical</span>
                        <span className="stat-value-modern critical">
                          {
                            allLogsReport.detailed_statistics.statistics
                              .critical_incidents
                          }
                        </span>
                      </div>
                      <div className="stat-item-modern">
                        <span className="stat-label-modern">High</span>
                        <span className="stat-value-modern high">
                          {
                            allLogsReport.detailed_statistics.statistics
                              .high_severity
                          }
                        </span>
                      </div>
                      <div className="stat-item-modern">
                        <span className="stat-label-modern">Medium</span>
                        <span className="stat-value-modern medium">
                          {
                            allLogsReport.detailed_statistics.statistics
                              .medium_severity
                          }
                        </span>
                      </div>
                      <div className="stat-item-modern">
                        <span className="stat-label-modern">Low</span>
                        <span className="stat-value-modern low">
                          {
                            allLogsReport.detailed_statistics.statistics
                              .low_severity
                          }
                        </span>
                      </div>
                      <div className="stat-item-modern">
                        <span className="stat-label-modern">
                          Avg. Anomaly Score
                        </span>
                        <span className="stat-value-modern">
                          {(
                            allLogsReport.detailed_statistics.statistics
                              .average_anomaly_score * 100
                          ).toFixed(2)}
                          %
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="report-section-modern">
                    <h4>🔍 Top Threats</h4>
                    <ul className="threats-list-modern">
                      {allLogsReport.detailed_statistics.top_threats.map(
                        (threat, idx) => (
                          <li key={idx}>
                            <span className="threat-name">{threat[0]}</span>
                            <span className="threat-count">
                              {threat[1]} occurrences
                            </span>
                          </li>
                        )
                      )}
                    </ul>
                  </div>

                  <div className="report-section-modern">
                    <h4>💡 Recommendations</h4>
                    <ul className="recommendations-list">
                      {allLogsReport.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default LogReports;
