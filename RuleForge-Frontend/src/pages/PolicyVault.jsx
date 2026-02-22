import React, { useState, useEffect } from 'react';
import {
  Search,
  Plus,
  Upload,
  Download,
  MoreVertical,
  Shield,
  CheckCircle,
  AlertCircle,
  Clock,
  FileText,
  Settings,
  Trash2,
  Edit,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import { fetchRules, getComplianceReportUrl } from '../services/api';
import './PolicyVault.css';

const categories = ['All', 'threshold', 'pattern', 'null_check', 'frequency', 'range', 'uniqueness', 'unknown'];

function PolicyVault() {
  const [rules, setRules] = useState([]);
  const [types, setTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [openMenuId, setOpenMenuId] = useState(null);
  const [expandedPolicyId, setExpandedPolicyId] = useState(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRules();
      setRules(data.rules || []);
      setTypes(['All', ...(data.types || [])]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const filteredRules = rules.filter(rule => {
    const matchesSearch =
      (rule.id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (rule.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (rule.condition_field || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || rule.rule_type === selectedCategory;
    const matchesStatus =
      selectedStatus === 'all' ||
      (selectedStatus === 'triggered' && rule.violations > 0) ||
      (selectedStatus === 'clear' && rule.violations === 0);
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const totalRules = rules.length;
  const triggeredRules = rules.filter(r => r.violations > 0).length;
  const totalViolations = rules.reduce((acc, r) => acc + (r.violations || 0), 0);

  if (loading) {
    return (
      <div className="policy-vault">
        <div className="loading-state">
          <RefreshCw size={32} className="spinning" />
          <p>Loading policy rules…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="policy-vault">
        <div className="error-state">
          <AlertTriangle size={32} />
          <h3>Failed to load rules</h3>
          <p>{error}</p>
          <p className="error-hint">Start the backend: <code>python flask_backend.py</code></p>
          <Button variant="primary" onClick={loadData}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="policy-vault">
      {/* Header Actions */}
      <div className="vault-header">
        <div className="vault-stats">
          <div className="stat-item">
            <span className="stat-value">{totalRules}</span>
            <span className="stat-label">Total Rules</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{triggeredRules}</span>
            <span className="stat-label">Triggered</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{totalViolations.toLocaleString()}</span>
            <span className="stat-label">Total Violations</span>
          </div>
        </div>

        <div className="vault-actions">
          <Button variant="ghost" icon={RefreshCw} size="sm" onClick={loadData}>
            Refresh
          </Button>
          <a href={getComplianceReportUrl()} download>
            <Button variant="secondary" icon={Download} size="sm">
              Export
            </Button>
          </a>
        </div>
      </div>

      {/* Filters */}
      <div className="vault-filters">
        <div className="search-wrapper">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search rules, fields, descriptions…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-tabs">
          {(types.length > 1 ? types : ['All', ...categories.slice(1)]).map(cat => (
            <button
              key={cat}
              className={`filter-tab ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>

        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="status-filter"
        >
          <option value="all">All Status</option>
          <option value="triggered">Triggered</option>
          <option value="clear">Clear</option>
        </select>
      </div>

      {/* No data state */}
      {rules.length === 0 && (
        <div className="empty-state">
          <Shield size={48} />
          <h3>No policy rules extracted yet</h3>
          <p>Upload a regulatory PDF and run <strong>Phase 1</strong> from the Scan Now page.</p>
        </div>
      )}

      {/* Policy Cards */}
      <div className="policy-grid">
        {filteredRules.map(rule => {
          const isTriggered = rule.violations > 0;
          const isExpanded = expandedPolicyId === rule.id;

          return (
            <div 
              key={rule.id} 
              className={`policy-card ${isExpanded ? 'expanded' : ''}`}
              onClick={() => setExpandedPolicyId(isExpanded ? null : rule.id)}
            >
              <div className="policy-card-header">
                <div className="policy-icon">
                  <Shield size={20} />
                </div>
                <div className="policy-meta">
                  <span className="policy-id">{rule.id}</span>
                  <Badge
                    variant={isTriggered ? (rule.violations >= 500 ? 'red' : rule.violations >= 50 ? 'orange' : 'green') : 'gray'}
                    size="sm"
                  >
                    {isTriggered ? `${rule.violations.toLocaleString()} violations` : 'Clear'}
                  </Badge>
                </div>
                <div className="policy-menu-wrapper">
                  <button
                    className="policy-menu-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenMenuId(openMenuId === rule.id ? null : rule.id);
                    }}
                  >
                    <MoreVertical size={18} />
                  </button>
                  {openMenuId === rule.id && (
                    <div className="policy-menu-dropdown">
                      <button onClick={(e) => {
                        e.stopPropagation();
                        setExpandedPolicyId(rule.id);
                        setOpenMenuId(null);
                      }}>
                        <FileText size={14} /> View Full Text
                      </button>
                      <button onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(rule.sql_hint || '');
                        setOpenMenuId(null);
                      }}>
                        <FileText size={14} /> Copy SQL Hint
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div className="policy-card-body">
                <h3 className="policy-name">{rule.condition_field || rule.id}</h3>
                <p className={`policy-description ${isExpanded ? 'expanded' : ''}`}>
                  {rule.description}
                </p>

                {isExpanded && (
                  <div className="policy-full-details">
                    <div className="detail-row">
                      <span className="detail-label">Rule Type:</span>
                      <span className="detail-value">{rule.rule_type || 'unknown'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Condition Field:</span>
                      <span className="detail-value">{rule.condition_field || '—'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Operator:</span>
                      <span className="detail-value">{rule.operator || '—'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Threshold Value:</span>
                      <span className="detail-value">{String(rule.threshold_value) || '—'}</span>
                    </div>
                    {rule.sql_hint && (
                      <div className="detail-row full-width">
                        <span className="detail-label">SQL Hint:</span>
                        <pre className="sql-hint-expanded">{rule.sql_hint}</pre>
                      </div>
                    )}
                  </div>
                )}

                {!isExpanded && (
                  <div className="policy-tags">
                    <Badge variant="blue" size="sm">{rule.rule_type || 'unknown'}</Badge>
                    <Badge variant="purple" size="sm">
                      {rule.operator} {rule.threshold_value}
                    </Badge>
                  </div>
                )}
              </div>

              <div className="policy-card-stats">
                <div className="policy-stat">
                  <FileText size={14} />
                  <span>{rule.condition_field || '—'}</span>
                </div>
                <div className={`policy-stat ${isTriggered ? 'violations' : ''}`}>
                  <AlertCircle size={14} />
                  <span>{(rule.violations || 0).toLocaleString()} violations</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredRules.length === 0 && rules.length > 0 && (
        <div className="empty-state">
          <Shield size={48} />
          <h3>No matching rules</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      )}
    </div>
  );
}

export default PolicyVault;
