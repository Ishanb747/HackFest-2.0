import React from 'react';
import './KPICard.css';

function KPICard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  variant = 'default',
  trend,
  trendValue 
}) {
  return (
    <div className={`kpi-card ${variant}`}>
      <div className="kpi-icon-wrapper">
        {Icon && <Icon size={24} />}
      </div>
      <div className="kpi-content">
        <span className="kpi-label">{title}</span>
        <div className="kpi-value-row">
          <span className="kpi-value">{value}</span>
          {trend && (
            <span className={`kpi-trend ${trend}`}>
              {trend === 'up' ? '↑' : '↓'} {trendValue}
            </span>
          )}
        </div>
        {subtitle && <span className="kpi-subtitle">{subtitle}</span>}
      </div>
    </div>
  );
}

export default KPICard;
