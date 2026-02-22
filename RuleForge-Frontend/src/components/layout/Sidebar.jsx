import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Shield,
  ScanLine,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  FileText,
  ClipboardList,
  Activity,
  GitCompare
} from 'lucide-react';
import './Sidebar.css';

const navItems = [
  { path: '/scan-now', label: 'Scan Now', icon: ScanLine },
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/policy-vault', label: 'Policy Vault', icon: Shield },
  { path: '/violations', label: 'Violations', icon: FileText },
  { path: '/policy-versions', label: 'Policy Versions', icon: GitCompare },
  { path: '/audit-log', label: 'Audit Log', icon: ClipboardList },
  { path: '/live-monitor', label: 'Live Monitor', icon: Activity, live: true },
  { path: '/configuration', label: 'Configuration', icon: Settings },
];

function Sidebar({ collapsed, onToggle, currentUser }) {
  const location = useLocation();

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="logo">
          <div className="logo-icon">
            <Shield size={24} />
          </div>
          {!collapsed && <span className="logo-text">RuleForge</span>}
        </div>
        <button
          className="collapse-btn"
          onClick={onToggle}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {!collapsed && (
        <div className="sidebar-section-label">NAVIGATION</div>
      )}

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <div className="nav-icon">
                <Icon size={20} />
              </div>
              {!collapsed && (
                <span className="nav-label">
                  {item.label}
                  {item.live && !collapsed && (
                    <span className="live-badge">LIVE</span>
                  )}
                </span>
              )}
              {isActive && <div className="active-indicator" />}
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="user-avatar">
            {currentUser.avatar ? (
              <img src={currentUser.avatar} alt={currentUser.name} />
            ) : (
              <span>{currentUser.name.charAt(0)}</span>
            )}
          </div>
          {!collapsed && (
            <div className="user-info">
              <span className="user-name">{currentUser.name}</span>
              <span className="user-role">{currentUser.role}</span>
            </div>
          )}
        </div>
        <button className="logout-btn">
          <LogOut size={18} />
          {!collapsed && <span>Sign Out</span>}
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
