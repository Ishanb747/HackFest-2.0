import React from 'react';
import { useLocation } from 'react-router-dom';
import { Search, Bell, Wifi } from 'lucide-react';
import './Header.css';

const pageTitles = {
  '/dashboard': { title: 'Violation Dashboard', subtitle: 'Monitor policy violations across all datasets' },
  '/policy-vault': { title: 'Policy Vault', subtitle: 'Manage and configure compliance policies' },
  '/violations': { title: 'Violations', subtitle: 'Review and resolve policy violations' },
  '/scan-now': { title: 'Scan Now', subtitle: 'Run policy scans on your datasets' },
  '/audit-log': { title: 'Audit Log', subtitle: 'View system activity and decisions' },
  '/configuration': { title: 'Configuration', subtitle: 'System settings and preferences' },
};

function Header() {
  const location = useLocation();
  const pageInfo = pageTitles[location.pathname] || { title: 'Dashboard', subtitle: '' };

  return (
    <header className="header">
      <div className="header-left">
        <div className="page-info">
          <h1 className="page-title">{pageInfo.title}</h1>
          <p className="page-subtitle">{pageInfo.subtitle}</p>
        </div>
      </div>

      <div className="header-right">
        <div className="search-box">
          <Search size={18} className="search-icon" />
          <input 
            type="text" 
            placeholder="Search violations, policies..." 
            className="search-input"
          />
        </div>

        <div className="header-actions">
          <button className="header-action-btn" aria-label="Notifications">
            <Bell size={20} />
            <span className="notification-badge">3</span>
          </button>
          
          <div className="live-indicator">
            <Wifi size={16} />
            <span>Live</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
