import React, { useState, useEffect } from 'react';
import {
  FileWarning,
  AlertTriangle,
  AlertCircle,
  CheckCircle,
  Shield,
  Filter,
  Eye,
  RefreshCw,
  Clock
} from 'lucide-react';
import KPICard from '../components/common/KPICard';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import DataTable from '../components/common/DataTable';
import SeverityBreakdown from '../components/dashboard/SeverityBreakdown';
import { fetchStats, fetchViolations } from '../services/api';
import './Dashboard.css';

const columns = [
  {
    header: 'Rule ID',
    accessor: 'rule_id',
    render: (value) => <span className="violation-id">{value}</span>
  },
  {
    header: 'Severity',
    accessor: 'severity',
    render: (value) => (
      <Badge variant={value.toLowerCase()}>{value}</Badge>
    )
  },
  {
    header: 'HITL Status',
    accessor: 'hitl_action',
    render: (value) => {
      const colorMap = {
        CONFIRMED: 'green',
        DISMISSED: 'gray',
        ESCALATED: 'purple',
        PENDING: 'orange',
      };
      return (
        <Badge variant={colorMap[value] || 'orange'}>{value}</Badge>
      );
    }
  },
  {
    header: 'Violations',
    accessor: 'violation_count',
    render: (value) => (
      <span style={{ fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
        {(value || 0).toLocaleString()}
      </span>
    )
  },
  {
    header: 'SQL Status',
    accessor: 'status',
    render: (value) => {
      const colorMap = { SUCCESS: 'green', BLOCKED: 'red', SQL_ERROR: 'orange', SKIPPED: 'gray' };
      return <Badge variant={colorMap[value] || 'blue'} className="status">{value}</Badge>;
    }
  },
  {
    header: 'Description',
    accessor: 'description',
    render: (value) => (
      <span className="dataset-name" title={value}>
        {value && value.length > 60 ? value.slice(0, 60) + '…' : value}
      </span>
    )
  },
];

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [severityFilter, setSeverityFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const PAGE_SIZE = 10;

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, vData] = await Promise.all([
        fetchStats(),
        fetchViolations({ sort: 'desc' }),
      ]);
      setStats(statsData);
      setViolations(vData.violations || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const filteredViolations = violations.filter(v => {
    if (severityFilter === 'all') return true;
    return v.severity.toLowerCase() === severityFilter;
  });

  const paginatedViolations = filteredViolations.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE
  );

  const totalPages = Math.ceil(filteredViolations.length / PAGE_SIZE);

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading-state">
          <RefreshCw size={32} className="spinning" />
          <p>Loading dashboard data…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <div className="error-state">
          <AlertTriangle size={32} />
          <h3>Failed to load data</h3>
          <p>{error}</p>
          <p className="error-hint">Make sure the Flask backend is running: <code>python flask_backend.py</code></p>
          <Button variant="primary" onClick={loadData}>Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPICard
          title="Total Violations"
          value={(stats?.total_violations || 0).toLocaleString()}
          subtitle="Across all rules"
          icon={FileWarning}
          variant="blue"
        />
        <KPICard
          title="High Severity"
          value={(stats?.high_severity || 0).toLocaleString()}
          subtitle="≥ 500 violations"
          icon={AlertTriangle}
          variant="red"
        />
        <KPICard
          title="Medium Severity"
          value={(stats?.medium_severity || 0).toLocaleString()}
          subtitle="50–499 violations"
          icon={AlertCircle}
          variant="orange"
        />
        <KPICard
          title="Low Severity"
          value={(stats?.low_severity || 0).toLocaleString()}
          subtitle="< 50 violations"
          icon={CheckCircle}
          variant="cyan"
        />
        <KPICard
          title="Policies Active"
          value={stats?.total_rules || 0}
          subtitle={`${stats?.rules_triggered || 0} rule(s) triggered`}
          icon={Shield}
          variant="purple"
        />
      </div>

      {/* Severity Breakdown */}
      <SeverityBreakdown
        high={stats?.high_severity || 0}
        medium={stats?.medium_severity || 0}
        low={stats?.low_severity || 0}
      />

      {/* Pie Chart - Rule Type Distribution */}
      <div className="chart-section">
        <h3 className="chart-title">Rule Type Distribution</h3>
        <div className="pie-chart-container">
          {(() => {
            const typeCounts = {};
            violations.forEach(v => {
              const type = v.description?.match(/\b(threshold|pattern|frequency|jurisdiction|ratio|null_check|range|uniqueness)\b/i)?.[0]?.toLowerCase() || 'unknown';
              typeCounts[type] = (typeCounts[type] || 0) + 1;
            });
            
            const total = Object.values(typeCounts).reduce((a, b) => a + b, 0);
            const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#6366f1', '#ef4444'];
            
            let cumulativePercent = 0;
            const segments = Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).map(([type, count], i) => {
              const percent = (count / total) * 100;
              const startPercent = cumulativePercent;
              cumulativePercent += percent;
              return { type, count, percent, startPercent, color: colors[i % colors.length] };
            });

            return (
              <>
                <svg className="pie-chart" viewBox="0 0 200 200">
                  <circle cx="100" cy="100" r="90" fill="var(--bg-tertiary)" />
                  {segments.map((seg, i) => {
                    const startAngle = (seg.startPercent / 100) * 360 - 90;
                    const endAngle = ((seg.startPercent + seg.percent) / 100) * 360 - 90;
                    const largeArc = seg.percent > 50 ? 1 : 0;
                    
                    const x1 = 100 + 80 * Math.cos((startAngle * Math.PI) / 180);
                    const y1 = 100 + 80 * Math.sin((startAngle * Math.PI) / 180);
                    const x2 = 100 + 80 * Math.cos((endAngle * Math.PI) / 180);
                    const y2 = 100 + 80 * Math.sin((endAngle * Math.PI) / 180);
                    
                    return (
                      <path
                        key={seg.type}
                        d={`M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`}
                        fill={seg.color}
                        stroke="var(--bg-card)"
                        strokeWidth="2"
                      />
                    );
                  })}
                  <circle cx="100" cy="100" r="50" fill="var(--bg-card)" />
                </svg>
                <div className="pie-legend">
                  {segments.map(seg => (
                    <div key={seg.type} className="legend-item">
                      <div className="legend-color" style={{ backgroundColor: seg.color }} />
                      <span className="legend-label">{seg.type}</span>
                      <span className="legend-value">{seg.count} ({seg.percent.toFixed(1)}%)</span>
                    </div>
                  ))}
                </div>
              </>
            );
          })()}
        </div>
      </div>

      {/* Last Run + Refresh */}
      <div className="dashboard-meta">
        <span className="last-run">
          <Clock size={14} />
          Last pipeline run: <strong>{stats?.last_run || 'Never'}</strong>
        </span>
        <Button variant="ghost" size="sm" icon={RefreshCw} onClick={loadData}>
          Refresh
        </Button>
      </div>

      {/* Violation Records */}
      <div className="violations-section">
        <div className="section-header">
          <div className="section-title-group">
            <h2 className="section-title">Violation Records</h2>
            <span className="section-subtitle">
              {filteredViolations.length} of {violations.length} rules
            </span>
          </div>

          <div className="section-filters">
            <div className="filter-group">
              <Filter size={16} />
              <select
                value={severityFilter}
                onChange={(e) => { setSeverityFilter(e.target.value); setCurrentPage(1); }}
                className="filter-select"
              >
                <option value="all">All Severities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
                <option value="clear">Clear</option>
              </select>
            </div>
          </div>
        </div>

        {violations.length === 0 ? (
          <div className="empty-state-dashboard">
            <Shield size={48} />
            <h3>No violation data yet</h3>
            <p>Upload a regulatory PDF and run the pipeline from the <strong>Scan Now</strong> page.</p>
          </div>
        ) : (
          <DataTable
            columns={columns}
            data={paginatedViolations}
            showCheckbox={false}
            pagination={{
              from: (currentPage - 1) * PAGE_SIZE + 1,
              to: Math.min(currentPage * PAGE_SIZE, filteredViolations.length),
              total: filteredViolations.length,
              currentPage,
              totalPages,
            }}
            onPageChange={setCurrentPage}
          />
        )}
      </div>
    </div>
  );
}

export default Dashboard;
