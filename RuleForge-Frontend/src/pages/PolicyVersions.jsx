import React, { useState, useEffect } from 'react';
import {
    GitCompare,
    Clock,
    FileText,
    Shield,
    RefreshCw,
    AlertTriangle,
    ChevronDown,
    ChevronRight,
    Plus,
    Minus,
    Equal,
    Download,
    Tag,
} from 'lucide-react';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { fetchVersions, getComplianceReportUrl } from '../services/api';
import './PolicyVersions.css';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

async function fetchVersionRules(versionNum) {
    const res = await fetch(`${BASE_URL}/api/versions/${versionNum}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

function diffRules(rulesA, rulesB) {
    const mapA = new Map(rulesA.map(r => [r._fingerprint || r.id, r]));
    const mapB = new Map(rulesB.map(r => [r._fingerprint || r.id, r]));

    const added = [...mapB.values()].filter(r => !mapA.has(r._fingerprint || r.id));
    const removed = [...mapA.values()].filter(r => !mapB.has(r._fingerprint || r.id));
    const same = [...mapA.values()].filter(r => mapB.has(r._fingerprint || r.id));

    return { added, removed, same };
}

function RuleRow({ rule, kind }) {
    const [open, setOpen] = useState(false);
    const icons = { added: Plus, removed: Minus, same: Equal };
    const Icon = icons[kind];
    return (
        <div className={`diff-row diff-${kind}`}>
            <button className="diff-row-header" onClick={() => setOpen(!open)}>
                <span className={`diff-kind-icon ${kind}`}><Icon size={14} /></span>
                <span className="diff-rule-id">{rule.id}</span>
                <span className="diff-rule-desc">{rule.description}</span>
                <Badge variant={kind === 'added' ? 'green' : kind === 'removed' ? 'red' : 'gray'} size="sm">
                    {rule.rule_type || '—'}
                </Badge>
                {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
            {open && (
                <div className="diff-row-detail">
                    <div className="diff-detail-grid">
                        <div><span className="dl">Field</span><span className="dv">{rule.condition_field}</span></div>
                        <div><span className="dl">Operator</span><span className="dv">{rule.operator}</span></div>
                        <div><span className="dl">Threshold</span><span className="dv">{String(rule.threshold_value)}</span></div>
                    </div>
                    {rule.sql_hint && (
                        <pre className="diff-sql">{rule.sql_hint}</pre>
                    )}
                </div>
            )}
        </div>
    );
}

function PolicyVersions() {
    const [versions, setVersions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Compare state
    const [leftVer, setLeftVer] = useState('current');
    const [rightVer, setRightVer] = useState(null);
    const [leftData, setLeftData] = useState(null);
    const [rightData, setRightData] = useState(null);
    const [comparing, setComparing] = useState(false);
    const [diff, setDiff] = useState(null);

    const loadVersions = async () => {
        setLoading(true);
        try {
            const data = await fetchVersions();
            setVersions(data.versions || []);
            if ((data.versions || []).length > 0) {
                setRightVer(data.versions[0].version);
            }
        } catch (e) { setError(e.message); }
        finally { setLoading(false); }
    };

    useEffect(() => { loadVersions(); }, []);

    const runCompare = async () => {
        if (!rightVer) return;
        setComparing(true);
        setDiff(null);
        try {
            // Left side — fetch current or a version
            const leftRes = leftVer === 'current'
                ? await fetch(`${BASE_URL}/api/rules`).then(r => r.json()).then(d => ({ rules: d.rules, version: 'current', timestamp: 'Now' }))
                : await fetchVersionRules(Number(leftVer));

            // Right side — always a version
            const rightRes = await fetchVersionRules(Number(rightVer));

            setLeftData(leftRes);
            setRightData(rightRes);
            setDiff(diffRules(leftRes.rules || [], rightRes.rules || []));
        } catch (e) {
            setError(e.message);
        } finally {
            setComparing(false);
        }
    };

    const formatDate = (ts) => {
        if (!ts || ts === 'Now') return 'Current';
        return new Date(ts).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="policy-versions-page">
                <div className="loading-state">
                    <RefreshCw size={32} className="spinning" />
                    <p>Loading version history…</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="policy-versions-page">
                <div className="error-state">
                    <AlertTriangle size={32} />
                    <h3>Failed to load versions</h3>
                    <p>{error}</p>
                    <Button variant="primary" onClick={loadVersions}>Retry</Button>
                </div>
            </div>
        );
    }

    return (
        <div className="policy-versions-page">
            {/* Version Timeline */}
            <section className="versions-timeline-section">
                <div className="section-hdr">
                    <h2 className="section-ttl">
                        <Tag size={18} />
                        Version History
                    </h2>
                    <div className="section-actions">
                        <Button variant="ghost" size="sm" icon={RefreshCw} onClick={loadVersions}>
                            Refresh
                        </Button>
                        <a href={getComplianceReportUrl()} download>
                            <Button variant="secondary" icon={Download} size="sm">Export</Button>
                        </a>
                    </div>
                </div>

                {versions.length === 0 ? (
                    <div className="empty-versions">
                        <FileText size={40} />
                        <h3>No archived versions yet</h3>
                        <p>A new version is archived automatically every time you run Phase 1 with a new or different PDF.</p>
                    </div>
                ) : (
                    <div className="versions-list">
                        {versions.map((v, i) => (
                            <div key={v.version} className={`version-item ${i === 0 ? 'latest' : ''}`}>
                                <div className="version-marker">
                                    <div className="version-dot" />
                                    {i < versions.length - 1 && <div className="version-line" />}
                                </div>
                                <div className="version-content">
                                    <div className="version-header">
                                        <div className="version-badges">
                                            <span className="version-num">v{v.version}</span>
                                            {i === 0 && <Badge variant="green" size="sm">Latest Archive</Badge>}
                                        </div>
                                        <span className="version-date">{formatDate(v.timestamp)}</span>
                                    </div>
                                    <div className="version-meta">
                                        <div className="vmeta-item">
                                            <Shield size={13} />
                                            {v.rule_count} rules
                                        </div>
                                        {v.pdf_source && v.pdf_source !== 'unknown' && (
                                            <div className="vmeta-item">
                                                <FileText size={13} />
                                                {v.pdf_source}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                        <div className="version-item">
                            <div className="version-marker">
                                <div className="version-dot current" />
                            </div>
                            <div className="version-content">
                                <div className="version-header">
                                    <div className="version-badges">
                                        <span className="version-num">Current</span>
                                        <Badge variant="blue" size="sm">Active</Badge>
                                    </div>
                                </div>
                                <p className="version-current-hint">The live policy_rules.json in use right now</p>
                            </div>
                        </div>
                    </div>
                )}
            </section>

            {/* Compare Panel */}
            {versions.length > 0 && (
                <section className="compare-section">
                    <div className="section-hdr">
                        <h2 className="section-ttl">
                            <GitCompare size={18} />
                            Compare Versions
                        </h2>
                    </div>

                    <div className="compare-controls">
                        <div className="compare-select-group">
                            <label className="cmp-label">Left (Base)</label>
                            <select
                                className="cmp-select"
                                value={leftVer}
                                onChange={e => setLeftVer(e.target.value)}
                            >
                                <option value="current">Current (live)</option>
                                {versions.map(v => (
                                    <option key={v.version} value={v.version}>
                                        v{v.version} — {formatDate(v.timestamp)} ({v.rule_count} rules)
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="compare-arrow">
                            <GitCompare size={20} />
                        </div>

                        <div className="compare-select-group">
                            <label className="cmp-label">Right (Compare To)</label>
                            <select
                                className="cmp-select"
                                value={rightVer || ''}
                                onChange={e => setRightVer(Number(e.target.value))}
                            >
                                {versions.map(v => (
                                    <option key={v.version} value={v.version}>
                                        v{v.version} — {formatDate(v.timestamp)} ({v.rule_count} rules)
                                    </option>
                                ))}
                            </select>
                        </div>

                        <Button
                            variant="primary"
                            icon={GitCompare}
                            onClick={runCompare}
                            loading={comparing}
                            disabled={comparing || !rightVer}
                        >
                            {comparing ? 'Comparing…' : 'Compare'}
                        </Button>
                    </div>

                    {/* Diff Results */}
                    {diff && (
                        <div className="diff-result">
                            <div className="diff-summary">
                                <div className="diff-summary-card added">
                                    <Plus size={16} />
                                    <span>{diff.added.length} Added in right</span>
                                </div>
                                <div className="diff-summary-card removed">
                                    <Minus size={16} />
                                    <span>{diff.removed.length} Only in left</span>
                                </div>
                                <div className="diff-summary-card same">
                                    <Equal size={16} />
                                    <span>{diff.same.length} Unchanged</span>
                                </div>
                            </div>

                            <div className="diff-legend">
                                Comparing <strong>{leftVer === 'current' ? 'Current' : `v${leftVer}`}</strong>
                                {' '}({leftData?.rule_count ?? '?'} rules) vs{' '}
                                <strong>v{rightVer}</strong> ({rightData?.rule_count ?? '?'} rules)
                            </div>

                            <div className="diff-list">
                                {diff.added.length > 0 && (
                                    <div className="diff-group">
                                        <div className="diff-group-header added">
                                            <Plus size={14} /> {diff.added.length} rules only in <strong>right</strong>
                                        </div>
                                        {diff.added.map(r => <RuleRow key={r.id} rule={r} kind="added" />)}
                                    </div>
                                )}
                                {diff.removed.length > 0 && (
                                    <div className="diff-group">
                                        <div className="diff-group-header removed">
                                            <Minus size={14} /> {diff.removed.length} rules only in <strong>left</strong>
                                        </div>
                                        {diff.removed.map(r => <RuleRow key={r.id} rule={r} kind="removed" />)}
                                    </div>
                                )}
                                {diff.same.length > 0 && (
                                    <div className="diff-group">
                                        <div className="diff-group-header same">
                                            <Equal size={14} /> {diff.same.length} unchanged rules
                                        </div>
                                        {diff.same.map(r => <RuleRow key={r.id} rule={r} kind="same" />)}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </section>
            )}
        </div>
    );
}

export default PolicyVersions;
