import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Download,
  Eye,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  ChevronDown,
  ExternalLink,
  Database,
  Calendar,
  RefreshCw,
  Shield,
  Info,
} from 'lucide-react';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { fetchViolations, submitHITLDecision, getViolationsCSVUrl } from '../services/api';
import './Violations.css';

const statusConfig = {
  PENDING: { label: 'Pending Review', color: 'orange', icon: Clock },
  CONFIRMED: { label: 'Confirmed', color: 'red', icon: AlertTriangle },
  DISMISSED: { label: 'Dismissed', color: 'gray', icon: XCircle },
  ESCALATED: { label: 'Escalated', color: 'purple', icon: ExternalLink },
};

function Violations() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [expandedId, setExpandedId] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  const [toast, setToast] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchViolations({ sort: 'desc' });
      setViolations(data.violations || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleAction = async (action, ruleId) => {
    setActionLoading(`${action}-${ruleId}`);
    try {
      await submitHITLDecision(ruleId, action.toUpperCase());
      showToast(`Rule ${ruleId} ${action.toLowerCase()}d`, 'success');
      await loadData(); // Refresh
    } catch (e) {
      showToast(`Failed: ${e.message}`, 'error');
    } finally {
      setActionLoading(null);
    }
  };

  const filteredViolations = violations.filter(v => {
    const matchesSearch =
      v.rule_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      v.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === 'all' || v.severity.toLowerCase() === severityFilter;
    const matchesStatus = statusFilter === 'all' || v.hitl_action === statusFilter;
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const formatDate = (dateString) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="violations-page">
        <div className="loading-state">
          <RefreshCw size={32} className="spinning" />
          <p>Loading violations…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="violations-page">
        <div className="error-state">
          <AlertTriangle size={32} />
          <h3>Failed to load violations</h3>
          <p>{error}</p>
          <p className="error-hint">Start the backend: <code>python flask_backend.py</code></p>
          <Button variant="primary" onClick={loadData}>Retry</Button>
        </div>
      </div>
    );
  }

  const pending = violations.filter(v => v.hitl_action === 'PENDING').length;
  const highSev = violations.filter(v => v.severity === 'HIGH').length;
  const confirmed = violations.filter(v => v.hitl_action === 'CONFIRMED').length;
  const escalated = violations.filter(v => v.hitl_action === 'ESCALATED').length;

  return (
    <div className="violations-page">
      {/* Toast notification */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
          {toast.message}
        </div>
      )}

      {/* Summary Stats */}
      <div className="violations-summary">
        <div className="summary-card">
          <div className="summary-icon pending"><Clock size={20} /></div>
          <div className="summary-content">
            <span className="summary-value">{pending}</span>
            <span className="summary-label">Pending Review</span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon high"><AlertTriangle size={20} /></div>
          <div className="summary-content">
            <span className="summary-value">{highSev}</span>
            <span className="summary-label">High Severity</span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon confirmed"><CheckCircle size={20} /></div>
          <div className="summary-content">
            <span className="summary-value">{confirmed}</span>
            <span className="summary-label">Confirmed</span>
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-icon escalated"><ExternalLink size={20} /></div>
          <div className="summary-content">
            <span className="summary-value">{escalated}</span>
            <span className="summary-label">Escalated</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="violations-filters">
        <div className="search-wrapper">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search rule ID or description…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <Filter size={16} />
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Severities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="clear">Clear</option>
          </select>
        </div>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="PENDING">Pending</option>
          <option value="CONFIRMED">Confirmed</option>
          <option value="DISMISSED">Dismissed</option>
          <option value="ESCALATED">Escalated</option>
        </select>

        <Button
          variant="ghost"
          size="sm"
          icon={RefreshCw}
          onClick={loadData}
        >
          Refresh
        </Button>

        <a href={getViolationsCSVUrl()} download>
          <Button variant="secondary" icon={Download} size="sm">
            Export CSV
          </Button>
        </a>
      </div>

      {/* No data yet */}
      {violations.length === 0 && (
        <div className="empty-state">
          <Shield size={48} />
          <h3>No violations found</h3>
          <p>Run the pipeline from the <strong>Scan Now</strong> page to detect violations.</p>
        </div>
      )}

      {/* Violations List */}
      <div className="violations-list">
        {filteredViolations.map(violation => {
          const hitlStatus = violation.hitl_action || 'PENDING';
          const statusInfo = statusConfig[hitlStatus] || statusConfig.PENDING;
          const StatusIcon = statusInfo.icon;
          const isExpanded = expandedId === violation.rule_id;
          const isActioning = actionLoading && actionLoading.includes(violation.rule_id);

          return (
            <div
              key={violation.rule_id}
              className={`violation-card ${violation.severity.toLowerCase()} ${isExpanded ? 'expanded' : ''}`}
            >
              <div
                className="violation-header"
                onClick={() => setExpandedId(isExpanded ? null : violation.rule_id)}
              >
                <div className="violation-main">
                  <div className="violation-id-group">
                    <span className="violation-id">{violation.rule_id}</span>
                    <Badge variant={violation.severity.toLowerCase()} size="sm">
                      {violation.severity}
                    </Badge>
                    <Badge variant={statusInfo.color} size="sm">
                      <StatusIcon size={12} />
                      {statusInfo.label}
                    </Badge>
                    {violation.generated_by === 'llm' && (
                      <Badge variant="blue" size="sm">🤖 AI Explained</Badge>
                    )}
                  </div>
                  <h3 className="violation-title">{violation.rule_id}</h3>
                  <p className="violation-desc">
                    {violation.plain_english || violation.description}
                  </p>
                </div>

                <div className="violation-meta">
                  <div className="meta-item">
                    <Database size={14} />
                    <span>{(violation.violation_count || 0).toLocaleString()} records</span>
                  </div>
                  {violation.hitl_timestamp && (
                    <div className="meta-item">
                      <Calendar size={14} />
                      <span>{formatDate(violation.hitl_timestamp)}</span>
                    </div>
                  )}
                </div>

                <button className={`expand-btn ${isExpanded ? 'expanded' : ''}`}>
                  <ChevronDown size={20} />
                </button>
              </div>

              {isExpanded && (
                <div className="violation-details">
                  <div className="details-grid">
                    <div className="detail-item">
                      <span className="detail-label">Rule ID</span>
                      <span className="detail-value">{violation.rule_id}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">SQL Status</span>
                      <span className="detail-value">{violation.status}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Violation Count</span>
                      <span className="detail-value highlight">
                        {(violation.violation_count || 0).toLocaleString()}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">HITL Analyst</span>
                      <span className="detail-value">{violation.hitl_analyst || '—'}</span>
                    </div>
                    {violation.recommended_action && (
                      <div className="detail-item">
                        <span className="detail-label">Recommended Action</span>
                        <span className="detail-value">{violation.recommended_action}</span>
                      </div>
                    )}
                    {violation.policy_reference && (
                      <div className="detail-item">
                        <span className="detail-label">Policy Reference</span>
                        <span className="detail-value">{violation.policy_reference}</span>
                      </div>
                    )}
                    {violation.sql && (
                      <div className="detail-item full-width">
                        <span className="detail-label">SQL Used</span>
                        <pre className="detail-value code sql-block">{violation.sql}</pre>
                      </div>
                    )}
                    {violation.reason && (
                      <div className="detail-item full-width">
                        <span className="detail-label">Reason (blocked/error)</span>
                        <span className="detail-value">{violation.reason}</span>
                      </div>
                    )}
                    {violation.sample_violations && violation.sample_violations.length > 0 && (
                      <div className="detail-item full-width">
                        <span className="detail-label">Sample Records</span>
                        <div className="sample-table-wrap">
                          <table className="sample-table">
                            <thead>
                              <tr>
                                {Object.keys(violation.sample_violations[0]).map(k => (
                                  <th key={k}>{k}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {violation.sample_violations.map((row, i) => (
                                <tr key={i}>
                                  {Object.values(row).map((val, j) => (
                                    <td key={j}>{String(val)}</td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="violation-actions">
                    <Button
                      variant="success"
                      size="sm"
                      icon={CheckCircle}
                      onClick={() => handleAction('CONFIRMED', violation.rule_id)}
                      loading={isActioning && actionLoading.startsWith('CONFIRMED')}
                      disabled={!!isActioning}
                    >
                      Confirm
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={XCircle}
                      onClick={() => handleAction('DISMISSED', violation.rule_id)}
                      loading={isActioning && actionLoading.startsWith('DISMISSED')}
                      disabled={!!isActioning}
                    >
                      Dismiss
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      icon={ExternalLink}
                      onClick={() => handleAction('ESCALATED', violation.rule_id)}
                      loading={isActioning && actionLoading.startsWith('ESCALATED')}
                      disabled={!!isActioning}
                    >
                      Escalate
                    </Button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {filteredViolations.length === 0 && violations.length > 0 && (
        <div className="empty-state">
          <AlertTriangle size={48} />
          <h3>No matching violations</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
}

export default Violations;
