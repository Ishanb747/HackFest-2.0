import React, { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import GateGuard from './components/common/GateGuard';
import { ScanProvider } from './context/ScanContext';
import Dashboard from './pages/Dashboard';
import PolicyVault from './pages/PolicyVault';
import ScanNow from './pages/ScanNow';
import PolicyVersions from './pages/PolicyVersions';
import Configuration from './pages/Configuration';
import Violations from './pages/Violations';
import AuditLog from './pages/AuditLog';
import LiveMonitor from './pages/LiveMonitor';
import './styles/App.css';

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentUser] = useState({
    name: 'Sankalp Badoni',
    role: 'ADMIN',
    avatar: null
  });

  return (
    <ScanProvider>
      <div className={`app ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          currentUser={currentUser}
        />
        <div className="main-wrapper">
          <Header />
          <main className="main-content">
            <Routes>
              {/* Ungated — entry point, always accessible */}
              <Route path="/" element={<Navigate to="/scan-now" replace />} />
              <Route path="/scan-now" element={<ScanNow />} />
              <Route path="/configuration" element={<Configuration />} />

              {/* Gated — require a completed scan */}
              <Route path="/dashboard" element={<GateGuard><Dashboard /></GateGuard>} />
              <Route path="/policy-vault" element={<GateGuard><PolicyVault /></GateGuard>} />
              <Route path="/violations" element={<GateGuard><Violations /></GateGuard>} />
              <Route path="/audit-log" element={<GateGuard><AuditLog /></GateGuard>} />
              <Route path="/live-monitor" element={<GateGuard><LiveMonitor /></GateGuard>} />
              <Route path="/policy-versions" element={<GateGuard><PolicyVersions /></GateGuard>} />
            </Routes>
          </main>
        </div>
      </div>
    </ScanProvider>
  );
}

export default App;
