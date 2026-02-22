import React, { useState, useEffect, useRef } from 'react';
import {
    Activity,
    Database,
    AlertTriangle,
    CheckCircle,
    XCircle,
    RefreshCw,
    Play,
    Square,
    Zap,
    Clock,
    TrendingUp,
    Eye,
    Shield,
    Wifi,
    WifiOff,
} from 'lucide-react';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import { fetchLiveStatus } from '../services/api';
import './LiveMonitor.css';

const POLL_INTERVAL_MS = 4000; // Refresh every 4 seconds

function ProcessStatus({ label, running, icon: Icon }) {
    return (
        <div className={`process-card ${running ? 'running' : 'stopped'}`}>
            <div className={`process-icon ${running ? 'running' : 'stopped'}`}>
                <Icon size={22} />
            </div>
            <div className="process-info">
                <span className="process-name">{label}</span>
                <div className="process-status-row">
                    {running ? (
                        <>
                            <span className="pulse-dot" />
                            <span className="status-text running">Running</span>
                        </>
                    ) : (
                        <>
                            <XCircle size={12} />
                            <span className="status-text stopped">Not running</span>
                        </>
                    )}
                </div>
            </div>
            <Badge variant={running ? 'green' : 'gray'} size="sm">
                {running ? 'LIVE' : 'OFFLINE'}
            </Badge>
        </div>
    );
}

function LiveMonitor() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);
    const [connected, setConnected] = useState(true);
    const pollRef = useRef(null);

    const loadData = async (isBackground = false) => {
        if (!isBackground) setLoading(true);
        try {
            const result = await fetchLiveStatus();
            setData(result);
            setLastUpdated(new Date());
            setConnected(true);
            setError(null);
        } catch (e) {
            setConnected(false);
            if (!isBackground) setError(e.message);
        } finally {
            if (!isBackground) setLoading(false);
        }
    };

    useEffect(() => {
        loadData(false);
        pollRef.current = setInterval(() => loadData(true), POLL_INTERVAL_MS);
        return () => clearInterval(pollRef.current);
    }, []);

    const severity = (count) => {
        if (count === 0) return 'clear';
        if (count < 50) return 'low';
        if (count < 500) return 'medium';
        return 'high';
    };

    if (loading) {
        return (
            <div className="live-monitor-page">
                <div className="loading-state">
                    <RefreshCw size={32} className="spinning" />
                    <p>Connecting to live monitor…</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="live-monitor-page">
                <div className="error-state">
                    <WifiOff size={40} />
                    <h3>Cannot reach backend</h3>
                    <p>{error}</p>
                    <p className="error-hint">Start the Flask backend: <code>python flask_backend.py</code></p>
                    <Button variant="primary" onClick={() => loadData(false)}>Retry</Button>
                </div>
            </div>
        );
    }

    const {
        ingester_running,
        watchdog_running,
        live_transaction_count,
        live_violations = [],
        config = {},
        last_update,
    } = data || {};

    const triggeredCount = live_violations.filter(v => v.violation_count > 0).length;
    const totalViolationHits = live_violations.reduce((s, v) => s + (v.violation_count || 0), 0);
    const highSevCount = live_violations.filter(v => v.severity === 'HIGH').length;

    return (
        <div className="live-monitor-page">
            {/* Connection Status Bar */}
            <div className={`conn-bar ${connected ? 'connected' : 'disconnected'}`}>
                {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
                <span>{connected ? 'Live — auto-refreshing every 4s' : 'Connection lost — retrying…'}</span>
                {lastUpdated && (
                    <span className="conn-time">
                        Last update: {lastUpdated.toLocaleTimeString()}
                    </span>
                )}
                <Button variant="ghost" size="sm" icon={RefreshCw} onClick={() => loadData(false)}>
                    Refresh now
                </Button>
            </div>

            {/* Process Status */}
            <section className="monitor-section">
                <h2 className="monitor-section-title">
                    <Activity size={18} />
                    Service Status
                </h2>
                <div className="process-grid">
                    <ProcessStatus
                        label="Data Ingester"
                        running={ingester_running}
                        icon={Database}
                    />
                    <ProcessStatus
                        label="Watchdog Scanner"
                        running={watchdog_running}
                        icon={Eye}
                    />
                </div>

                {(!ingester_running || !watchdog_running) && (
                    <div className="service-hint">
                        <AlertTriangle size={14} />
                        <span>
                            Start the inactive services in separate terminals:
                            {!ingester_running && <> <code>python ingester.py</code></>}
                            {!watchdog_running && <> <code>python turgon_watchdog.py</code></>}
                        </span>
                    </div>
                )}
            </section>

            {/* Live KPI Cards */}
            <section className="monitor-section">
                <h2 className="monitor-section-title">
                    <TrendingUp size={18} />
                    Live Metrics
                </h2>
                <div className="live-kpi-grid">
                    <div className="live-kpi-card">
                        <div className="kpi-icon blue"><Database size={20} /></div>
                        <div className="kpi-content">
                            <span className="kpi-value">
                                {live_transaction_count != null
                                    ? live_transaction_count.toLocaleString()
                                    : '—'}
                            </span>
                            <span className="kpi-label">Live Transactions</span>
                        </div>
                    </div>
                    <div className="live-kpi-card">
                        <div className="kpi-icon orange"><AlertTriangle size={20} /></div>
                        <div className="kpi-content">
                            <span className="kpi-value">{triggeredCount}</span>
                            <span className="kpi-label">Rules Triggered</span>
                        </div>
                    </div>
                    <div className="live-kpi-card">
                        <div className="kpi-icon red"><Shield size={20} /></div>
                        <div className="kpi-content">
                            <span className="kpi-value">{totalViolationHits.toLocaleString()}</span>
                            <span className="kpi-label">Total Violation Hits</span>
                        </div>
                    </div>
                    <div className="live-kpi-card">
                        <div className="kpi-icon purple"><Zap size={20} /></div>
                        <div className="kpi-content">
                            <span className="kpi-value">{highSevCount}</span>
                            <span className="kpi-label">High Severity Rules</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* Config Info */}
            <section className="monitor-section config-strip">
                <h2 className="monitor-section-title">
                    <Clock size={18} />
                    Scan Intervals
                </h2>
                <div className="config-badges">
                    <div className="config-item">
                        <span className="config-label">Ingester batch size</span>
                        <span className="config-value">{config.batch_size ?? '—'} rows</span>
                    </div>
                    <div className="config-item">
                        <span className="config-label">Ingester interval</span>
                        <span className="config-value">{config.ingester_interval ?? '—'}s</span>
                    </div>
                    <div className="config-item">
                        <span className="config-label">Watchdog interval</span>
                        <span className="config-value">{config.watchdog_interval ?? '—'}s</span>
                    </div>
                    {last_update && (
                        <div className="config-item">
                            <span className="config-label">Last watchdog scan</span>
                            <span className="config-value">{last_update}</span>
                        </div>
                    )}
                </div>
            </section>

            {/* Live Violation Table */}
            <section className="monitor-section">
                <h2 className="monitor-section-title">
                    <Shield size={18} />
                    Live Violation Report
                    {triggeredCount > 0 && (
                        <Badge variant="red" size="sm">{triggeredCount} active</Badge>
                    )}
                </h2>

                {live_violations.length === 0 ? (
                    <div className="empty-live">
                        <CheckCircle size={40} />
                        <h3>No live violation data yet</h3>
                        <p>
                            {watchdog_running
                                ? 'Watchdog is running — violations will appear after the next scan cycle.'
                                : 'Start turgon_watchdog.py to begin scanning live transactions.'}
                        </p>
                    </div>
                ) : (
                    <div className="live-violations-table-wrap">
                        <table className="live-violations-table">
                            <thead>
                                <tr>
                                    <th>Rule ID</th>
                                    <th>Severity</th>
                                    <th>Violations</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {live_violations
                                    .sort((a, b) => (b.violation_count || 0) - (a.violation_count || 0))
                                    .map((v, i) => {
                                        const sev = severity(v.violation_count || 0);
                                        return (
                                            <tr key={v.rule_id || i} className={sev !== 'clear' ? 'row-triggered' : ''}>
                                                <td className="rule-id-cell">{v.rule_id || '—'}</td>
                                                <td>
                                                    <Badge variant={sev === 'clear' ? 'gray' : sev} size="sm">
                                                        {sev.toUpperCase()}
                                                    </Badge>
                                                </td>
                                                <td className="count-cell">
                                                    {(v.violation_count || 0).toLocaleString()}
                                                </td>
                                                <td>
                                                    <Badge
                                                        variant={v.status === 'SUCCESS' ? 'green' : v.status === 'BLOCKED' ? 'red' : 'gray'}
                                                        size="sm"
                                                    >
                                                        {v.status || '—'}
                                                    </Badge>
                                                </td>
                                            </tr>
                                        );
                                    })}
                            </tbody>
                        </table>
                    </div>
                )}
            </section>
        </div>
    );
}

export default LiveMonitor;
