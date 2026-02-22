import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Download,
  Clock,
  User,
  Shield,
  Database,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  FileText,
  Play,
  RefreshCw,
} from 'lucide-react';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { fetchAuditLog, getComplianceReportUrl } from '../services/api';
import './AuditLog.css';

const eventTypeConfig = {
  PIPELINE_RUN: { label: 'Pipeline', icon: Play, color: 'blue' },
  HITL_CONFIRMED: { label: 'Confirmed', icon: CheckCircle, color: 'green' },
  HITL_DISMISSED: { label: 'Dismissed', icon: XCircle, color: 'gray' },
  HITL_ESCALATED: { label: 'Escalated', icon: AlertTriangle, color: 'purple' },
  SQL_EXECUTION: { label: 'SQL Query', icon: Database, color: 'cyan' },
  SQL_BLOCKED: { label: 'Blocked', icon: Shield, color: 'red' },
  EXPLANATION_RUN: { label: 'AI Explain', icon: Eye, color: 'pink' },
  POLICY_UPDATE: { label: 'Policy Update', icon: FileText, color: 'orange' },
  LIVE_DETECTION: { label: 'Live Scan', icon: Eye, color: 'pink' },
};

function AuditLog() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [eventFilter, setEventFilter] = useState('all');
  const [selectedLog, setSelectedLog] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAuditLog(200);
      setLogs(data.logs || []);
      setStats(data.stats || {});
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const filteredLogs = logs.filter(log => {
    const detailStr = JSON.stringify(log.details || {}).toLowerCase();
    const matchSearch = (log.event_type || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (log.rule_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      detailStr.includes(searchTerm.toLowerCase());
    const matchEvent = eventFilter === 'all' || log.event_type === eventFilter;
    return matchSearch && matchEvent;
  });

  const formatTimestamp = (ts) => {
    if (!ts) return { date: '—', time: '—' };
    const date = new Date(ts);
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    };
  };

  const getEventInfo = (eventType) =>
    eventTypeConfig[eventType] || { label: eventType, icon: FileText, color: 'gray' };

  if (loading) {
    return (
      <div className="audit-log-page">
        <div className="loading-state">
          <RefreshCw size={32} className="spinning" />
          <p>Loading audit log…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="audit-log-page">
        <div className="error-state">
          <AlertTriangle size={32} />
          <h3>Failed to load audit log</h3>
          <p>{error}</p>
          <p className="error-hint">Start the backend: <code>python flask_backend.py</code></p>
          <Button variant="primary" onClick={loadData}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="audit-log-page">
      {/* Stats Summary */}
      <div className="audit-stats">
        <div className="stat-card">
          <span className="stat-value">{stats.total_events ?? logs.length}</span>
          <span className="stat-label">Total Events</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.hitl_decisions ?? 0}</span>
          <span className="stat-label">HITL Decisions</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{stats.pipeline_runs ?? 0}</span>
          <span className="stat-label">Pipeline Runs</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">
            {logs.filter(l => l.event_type === 'SQL_BLOCKED').length}
          </span>
          <span className="stat-label">Blocked Queries</span>
        </div>
      </div>

      {/* Filters */}
      <div className="audit-filters">
        <div className="search-wrapper">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search audit logs…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <Filter size={16} />
          <select
            value={eventFilter}
            onChange={(e) => setEventFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Events</option>
            <option value="PIPELINE_RUN">Pipeline Runs</option>
            <option value="HITL_CONFIRMED">Confirmations</option>
            <option value="HITL_DISMISSED">Dismissals</option>
            <option value="HITL_ESCALATED">Escalations</option>
            <option value="EXPLANATION_RUN">AI Explanations</option>
            <option value="SQL_BLOCKED">Blocked Queries</option>
          </select>
        </div>

        <Button variant="ghost" size="sm" icon={RefreshCw} onClick={loadData}>
          Refresh
        </Button>

        <a href={getComplianceReportUrl()} download>
          <Button variant="secondary" icon={Download} size="sm">
            Export Report
          </Button>
        </a>
      </div>

      {/* Audit Log Timeline + Details Panel */}
      <div className="audit-content">
        <div className="audit-timeline">
          {filteredLogs.length === 0 && (
            <div className="empty-state">
              <Clock size={48} />
              <h3>{logs.length === 0 ? 'No audit events yet' : 'No matching events'}</h3>
              <p>{logs.length === 0
                ? 'Run the pipeline to begin recording events.'
                : 'Try adjusting your search or filters.'
              }</p>
            </div>
          )}

          {filteredLogs.map((log, index) => {
            const eventInfo = getEventInfo(log.event_type);
            const Icon = eventInfo.icon;
            const { date, time } = formatTimestamp(log.ts);
            const isBlocked = log.event_type === 'SQL_BLOCKED';

            return (
              <div
                key={log.id}
                className={`timeline-item ${selectedLog === log.id ? 'selected' : ''}`}
                onClick={() => setSelectedLog(selectedLog === log.id ? null : log.id)}
              >
                <div className="timeline-marker">
                  <div className={`marker-icon ${eventInfo.color}`}>
                    <Icon size={16} />
                  </div>
                  {index < filteredLogs.length - 1 && <div className="timeline-line" />}
                </div>

                <div className="timeline-content">
                  <div className="timeline-header">
                    <div className="timeline-meta">
                      <span className="event-id">#{log.id}</span>
                      <Badge variant={eventInfo.color} size="sm">{eventInfo.label}</Badge>
                      {isBlocked && <Badge variant="red" size="sm">Blocked</Badge>}
                      {log.rule_id && (
                        <Badge variant="gray" size="sm">{log.rule_id}</Badge>
                      )}
                    </div>
                    <div className="timeline-time">
                      <span className="time-date">{date}</span>
                      <span className="time-clock">{time}</span>
                    </div>
                  </div>

                  <p className="timeline-details">
                    {log.details && typeof log.details === 'object'
                      ? JSON.stringify(log.details)
                        .replace(/[{}"]/g, '')
                        .replace(/,/g, ' · ')
                        .replace(/:/g, ': ')
                      : String(log.details || '')
                    }
                  </p>

                  <div className="timeline-footer">
                    {log.phase && (
                      <div className="footer-item">
                        <Play size={14} />
                        <span>{log.phase}</span>
                      </div>
                    )}
                    {log.rule_id && (
                      <div className="footer-item">
                        <Shield size={14} />
                        <span>{log.rule_id}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Details Panel */}
        {selectedLog && (() => {
          const log = logs.find(l => l.id === selectedLog);
          if (!log) return null;
          const eventInfo = getEventInfo(log.event_type);

          return (
            <div className="audit-details-panel">
              <h3 className="panel-title">Event Details</h3>
              <div className="details-content">
                <div className="detail-row">
                  <span className="detail-label">Event ID</span>
                  <span className="detail-value">#{log.id}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Type</span>
                  <Badge variant={eventInfo.color}>{eventInfo.label}</Badge>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Timestamp</span>
                  <span className="detail-value">{log.ts}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Phase</span>
                  <span className="detail-value">{log.phase || '—'}</span>
                </div>
                {log.rule_id && (
                  <div className="detail-row">
                    <span className="detail-label">Rule ID</span>
                    <span className="detail-value code">{log.rule_id}</span>
                  </div>
                )}
                <div className="detail-row full">
                  <span className="detail-label">Details</span>
                  <pre className="detail-text">
                    {JSON.stringify(log.details, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );
}

export default AuditLog;
