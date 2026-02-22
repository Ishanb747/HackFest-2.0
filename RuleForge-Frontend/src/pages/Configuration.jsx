import React, { useState } from 'react';
import { 
  Settings, 
  Database, 
  Key, 
  Bell, 
  Shield, 
  Users,
  Globe,
  Moon,
  Sun,
  Save,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Mail,
  Slack,
  Webhook
} from 'lucide-react';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import './Configuration.css';

function Configuration() {
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    // General
    theme: 'dark',
    language: 'en',
    timezone: 'UTC',
    
    // Database
    dbHost: 'localhost',
    dbPort: '5432',
    dbName: 'RuleForge_db',
    connectionStatus: 'connected',
    
    // API
    apiEndpoint: 'https://api.RuleForge.com/v1',
    apiKey: '••••••••••••••••',
    rateLimit: '1000',
    
    // Notifications
    emailEnabled: true,
    slackEnabled: false,
    webhookEnabled: true,
    emailRecipients: 'admin@example.com',
    slackWebhook: '',
    webhookUrl: 'https://webhook.example.com/notifications',
    
    // Security
    sessionTimeout: '30',
    mfaEnabled: true,
    ipWhitelist: '',
    
    // Monitoring
    batchSize: '50',
    scanInterval: '15',
    retentionDays: '90',
  });

  const [isSaving, setIsSaving] = useState(false);

  const handleInputChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
  };

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'database', label: 'Database', icon: Database },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'monitoring', label: 'Monitoring', icon: RefreshCw },
  ];

  return (
    <div className="configuration-page">
      {/* Tabs */}
      <div className="config-tabs">
        {tabs.map(tab => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              className={`config-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <Icon size={18} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="config-content">
        {/* General Settings */}
        {activeTab === 'general' && (
          <div className="config-section">
            <div className="section-header">
              <h2 className="section-title">General Settings</h2>
              <p className="section-desc">Configure basic application preferences</p>
            </div>

            <div className="settings-grid">
              <div className="setting-item">
                <label className="setting-label">Theme</label>
                <div className="theme-toggle">
                  <button 
                    className={`theme-btn ${settings.theme === 'light' ? 'active' : ''}`}
                    onClick={() => handleInputChange('theme', 'light')}
                  >
                    <Sun size={16} />
                    Light
                  </button>
                  <button 
                    className={`theme-btn ${settings.theme === 'dark' ? 'active' : ''}`}
                    onClick={() => handleInputChange('theme', 'dark')}
                  >
                    <Moon size={16} />
                    Dark
                  </button>
                </div>
              </div>

              <div className="setting-item">
                <label className="setting-label">Language</label>
                <select 
                  className="setting-select"
                  value={settings.language}
                  onChange={(e) => handleInputChange('language', e.target.value)}
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>

              <div className="setting-item">
                <label className="setting-label">Timezone</label>
                <select 
                  className="setting-select"
                  value={settings.timezone}
                  onChange={(e) => handleInputChange('timezone', e.target.value)}
                >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time</option>
                  <option value="America/Los_Angeles">Pacific Time</option>
                  <option value="Europe/London">London</option>
                  <option value="Asia/Tokyo">Tokyo</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Database Settings */}
        {activeTab === 'database' && (
          <div className="config-section">
            <div className="section-header">
              <h2 className="section-title">Database Configuration</h2>
              <p className="section-desc">Manage database connection settings</p>
            </div>

            <div className="connection-status">
              <div className={`status-indicator ${settings.connectionStatus}`}>
                {settings.connectionStatus === 'connected' ? (
                  <CheckCircle size={20} />
                ) : (
                  <AlertCircle size={20} />
                )}
                <span>
                  {settings.connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <Button variant="secondary" size="sm" icon={RefreshCw}>
                Test Connection
              </Button>
            </div>

            <div className="settings-grid">
              <div className="setting-item">
                <label className="setting-label">Host</label>
                <input 
                  type="text"
                  className="setting-input"
                  value={settings.dbHost}
                  onChange={(e) => handleInputChange('dbHost', e.target.value)}
                />
              </div>

              <div className="setting-item">
                <label className="setting-label">Port</label>
                <input 
                  type="text"
                  className="setting-input"
                  value={settings.dbPort}
                  onChange={(e) => handleInputChange('dbPort', e.target.value)}
                />
              </div>

              <div className="setting-item">
                <label className="setting-label">Database Name</label>
                <input 
                  type="text"
                  className="setting-input"
                  value={settings.dbName}
                  onChange={(e) => handleInputChange('dbName', e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {/* API Settings */}
        {activeTab === 'api' && (
          <div className="config-section">
            <div className="section-header">
              <h2 className="section-title">API Configuration</h2>
              <p className="section-desc">Manage API endpoints and authentication</p>
            </div>

            <div className="settings-grid">
              <div className="setting-item full-width">
                <label className="setting-label">API Endpoint</label>
                <input 
                  type="text"
                  className="setting-input"
                  value={settings.apiEndpoint}
                  onChange={(e) => handleInputChange('apiEndpoint', e.target.value)}
                />
              </div>

              <div className="setting-item full-width">
                <label className="setting-label">API Key</label>
                <div className="input-with-action">
                  <input 
                    type="password"
                    className="setting-input"
                    value={settings.apiKey}
                    onChange={(e) => handleInputChange('apiKey', e.target.value)}
                  />
                  <Button variant="secondary" size="sm">
                    Regenerate
                  </Button>
                </div>
              </div>

              <div className="setting-item">
                <label className="setting-label">Rate Limit (requests/min)</label>
                <input 
                  type="number"
                  className="setting-input"
                  value={settings.rateLimit}
                  onChange={(e) => handleInputChange('rateLimit', e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {/* Notifications Settings */}
        {activeTab === 'notifications' && (
          <div className="config-section">
            <div className="section-header">
              <h2 className="section-title">Notification Settings</h2>
              <p className="section-desc">Configure alert channels and preferences</p>
            </div>

            <div className="notification-channels">
              <div className="channel-card">
                <div className="channel-header">
                  <div className="channel-icon email">
                    <Mail size={20} />
                  </div>
                  <div className="channel-info">
                    <span className="channel-name">Email Notifications</span>
                    <span className="channel-desc">Receive alerts via email</span>
                  </div>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox"
                      checked={settings.emailEnabled}
                      onChange={(e) => handleInputChange('emailEnabled', e.target.checked)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>
                {settings.emailEnabled && (
                  <div className="channel-config">
                    <input 
                      type="text"
                      className="setting-input"
                      placeholder="Recipients (comma-separated)"
                      value={settings.emailRecipients}
                      onChange={(e) => handleInputChange('emailRecipients', e.target.value)}
                    />
                  </div>
                )}
              </div>

              <div className="channel-card">
                <div className="channel-header">
                  <div className="channel-icon slack">
                    <Slack size={20} />
                  </div>
                  <div className="channel-info">
                    <span className="channel-name">Slack Integration</span>
                    <span className="channel-desc">Post alerts to Slack channels</span>
                  </div>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox"
                      checked={settings.slackEnabled}
                      onChange={(e) => handleInputChange('slackEnabled', e.target.checked)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>
                {settings.slackEnabled && (
                  <div className="channel-config">
                    <input 
                      type="text"
                      className="setting-input"
                      placeholder="Slack Webhook URL"
                      value={settings.slackWebhook}
                      onChange={(e) => handleInputChange('slackWebhook', e.target.value)}
                    />
                  </div>
                )}
              </div>

              <div className="channel-card">
                <div className="channel-header">
                  <div className="channel-icon webhook">
                    <Webhook size={20} />
                  </div>
                  <div className="channel-info">
                    <span className="channel-name">Webhook</span>
                    <span className="channel-desc">Send alerts to custom endpoints</span>
                  </div>
                  <label className="toggle-switch">
                    <input 
                      type="checkbox"
                      checked={settings.webhookEnabled}
                      onChange={(e) => handleInputChange('webhookEnabled', e.target.checked)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </div>
                {settings.webhookEnabled && (
                  <div className="channel-config">
                    <input 
                      type="text"
                      className="setting-input"
                      placeholder="Webhook URL"
                      value={settings.webhookUrl}
                      onChange={(e) => handleInputChange('webhookUrl', e.target.value)}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Security Settings */}
        {activeTab === 'security' && (
          <div className="config-section">
            <div className="section-header">
              <h2 className="section-title">Security Settings</h2>
              <p className="section-desc">Configure authentication and access controls</p>
            </div>

            <div className="settings-grid">
              <div className="setting-item">
                <label className="setting-label">Session Timeout (minutes)</label>
                <input 
                  type="number"
                  className="setting-input"
                  value={settings.sessionTimeout}
                  onChange={(e) => handleInputChange('sessionTimeout', e.target.value)}
                />
              </div>

              <div className="setting-item">
                <label className="setting-label">Multi-Factor Authentication</label>
                <label className="toggle-switch inline">
                  <input 
                    type="checkbox"
                    checked={settings.mfaEnabled}
                    onChange={(e) => handleInputChange('mfaEnabled', e.target.checked)}
                  />
                  <span className="toggle-slider" />
                  <span className="toggle-label">
                    {settings.mfaEnabled ? 'Enabled' : 'Disabled'}
                  </span>
                </label>
              </div>

              <div className="setting-item full-width">
                <label className="setting-label">IP Whitelist (comma-separated)</label>
                <input 
                  type="text"
                  className="setting-input"
                  placeholder="e.g., 192.168.1.1, 10.0.0.0/24"
                  value={settings.ipWhitelist}
                  onChange={(e) => handleInputChange('ipWhitelist', e.target.value)}
                />
                <span className="setting-hint">Leave empty to allow all IPs</span>
              </div>
            </div>
          </div>
        )}

        {/* Monitoring Settings */}
        {activeTab === 'monitoring' && (
          <div className="config-section">
            <div className="section-header">
              <h2 className="section-title">Monitoring Configuration</h2>
              <p className="section-desc">Configure live monitoring parameters</p>
            </div>

            <div className="settings-grid">
              <div className="setting-item">
                <label className="setting-label">Batch Size</label>
                <input 
                  type="number"
                  className="setting-input"
                  value={settings.batchSize}
                  onChange={(e) => handleInputChange('batchSize', e.target.value)}
                />
                <span className="setting-hint">Records processed per cycle</span>
              </div>

              <div className="setting-item">
                <label className="setting-label">Scan Interval (seconds)</label>
                <input 
                  type="number"
                  className="setting-input"
                  value={settings.scanInterval}
                  onChange={(e) => handleInputChange('scanInterval', e.target.value)}
                />
                <span className="setting-hint">Time between monitoring cycles</span>
              </div>

              <div className="setting-item">
                <label className="setting-label">Data Retention (days)</label>
                <input 
                  type="number"
                  className="setting-input"
                  value={settings.retentionDays}
                  onChange={(e) => handleInputChange('retentionDays', e.target.value)}
                />
                <span className="setting-hint">How long to keep violation records</span>
              </div>
            </div>
          </div>
        )}

        {/* Save Button */}
        <div className="config-actions">
          <Button variant="secondary">
            Reset to Defaults
          </Button>
          <Button 
            variant="primary" 
            icon={Save}
            onClick={handleSave}
            loading={isSaving}
          >
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
}

export default Configuration;
