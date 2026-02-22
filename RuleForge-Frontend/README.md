# RuleForge - React Frontend

A professional React frontend for the RuleForge/RuleForge policy violation detection system.

## Features

- **Dashboard** - Real-time overview with KPI cards, severity breakdown, and recent violations
- **Policy Vault** - Browse, search, and manage compliance policies
- **Violations** - Detailed violation list with HITL (Human-in-the-Loop) actions
- **Scan Now** - Upload files and trigger compliance scans
- **Configuration** - System settings, API config, notifications, and security
- **Audit Log** - Timeline view of all system events and actions

## Tech Stack

- React 18.2
- React Router 6
- Lucide React Icons
- Recharts (for charts)
- Framer Motion (for animations)
- CSS Custom Properties (theming)

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The app will run at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── common/          # Reusable UI components
│   │   │   ├── Badge.jsx
│   │   │   ├── Button.jsx
│   │   │   ├── DataTable.jsx
│   │   │   └── KPICard.jsx
│   │   ├── dashboard/       # Dashboard-specific components
│   │   │   └── SeverityBreakdown.jsx
│   │   └── layout/          # Layout components
│   │       ├── Header.jsx
│   │       └── Sidebar.jsx
│   ├── pages/               # Page components
│   │   ├── Dashboard.jsx
│   │   ├── PolicyVault.jsx
│   │   ├── Violations.jsx
│   │   ├── ScanNow.jsx
│   │   ├── Configuration.jsx
│   │   └── AuditLog.jsx
│   ├── styles/
│   │   └── index.css        # Global styles & CSS variables
│   ├── App.jsx              # Main app with routing
│   └── index.js             # Entry point
└── package.json
```

## Connecting to Backend

This frontend is designed to work with the RuleForge/RuleForge backend. To connect:

1. Update API endpoints in your service layer
2. Replace mock data in pages with actual API calls
3. Configure authentication as needed

### API Endpoints to Implement

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/violations` | GET | Fetch all violations |
| `/api/policies` | GET | Fetch all policies |
| `/api/scan` | POST | Trigger new scan |
| `/api/hitl/approve` | POST | Approve HITL action |
| `/api/hitl/reject` | POST | Reject HITL action |
| `/api/audit-logs` | GET | Fetch audit logs |
| `/api/config` | GET/PUT | Get/Update configuration |

## Customization

### Theme Colors

Edit `src/styles/index.css` to customize the color palette:

```css
:root {
  --bg-primary: #0a0e17;
  --accent-blue: #3b82f6;
  --accent-red: #ef4444;
  /* ... */
}
```

### Adding New Pages

1. Create component in `src/pages/`
2. Add route in `App.jsx`
3. Add navigation item in `Sidebar.jsx`

## License

Proprietary - All rights reserved
