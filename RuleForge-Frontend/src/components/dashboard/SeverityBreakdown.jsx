import React from 'react';
import './SeverityBreakdown.css';

function SeverityBreakdown({ high = 0, medium = 0, low = 0 }) {
  const total = high + medium + low;
  const highPercent = total > 0 ? (high / total) * 100 : 0;
  const mediumPercent = total > 0 ? (medium / total) * 100 : 0;
  const lowPercent = total > 0 ? (low / total) * 100 : 0;

  return (
    <div className="severity-breakdown">
      <div className="severity-header">
        <h3 className="severity-title">Severity Breakdown</h3>
      </div>
      
      <div className="severity-bar">
        {highPercent > 0 && (
          <div 
            className="severity-segment high" 
            style={{ width: `${highPercent}%` }}
            title={`High: ${high.toLocaleString()}`}
          />
        )}
        {mediumPercent > 0 && (
          <div 
            className="severity-segment medium" 
            style={{ width: `${mediumPercent}%` }}
            title={`Medium: ${medium.toLocaleString()}`}
          />
        )}
        {lowPercent > 0 && (
          <div 
            className="severity-segment low" 
            style={{ width: `${lowPercent}%` }}
            title={`Low: ${low.toLocaleString()}`}
          />
        )}
      </div>

      <div className="severity-legend">
        <div className="legend-item">
          <span className="legend-dot high" />
          <span className="legend-label">High</span>
          <span className="legend-value">{high.toLocaleString()}</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot medium" />
          <span className="legend-label">Medium</span>
          <span className="legend-value">{medium.toLocaleString()}</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot low" />
          <span className="legend-label">Low</span>
          <span className="legend-value">{low.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

export default SeverityBreakdown;
