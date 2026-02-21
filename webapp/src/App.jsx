import { useState, useEffect } from 'react'
import './index.css'
import Dashboard from './pages/Dashboard'
import PersonaBuilder from './pages/PersonaBuilder'
import MicrositeBuilder from './pages/MicrositeBuilder'
import EngagementDashboard from './pages/EngagementDashboard'
import TriggerPanel from './pages/TriggerPanel'

const API_BASE = 'http://localhost:8000'

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'persona', label: 'Persona Builder', icon: '🧠' },
  { id: 'microsite', label: 'Microsite Builder', icon: '🌐' },
  { id: 'engagement', label: 'Engagement', icon: '📈' },
  { id: 'triggers', label: 'Triggers', icon: '🔔' },
]

export default function App() {
  const [activePage, setActivePage] = useState('dashboard')

  // Simple hash-based routing
  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash.slice(1) || 'dashboard'
      setActivePage(hash)
    }
    handleHash()
    window.addEventListener('hashchange', handleHash)
    return () => window.removeEventListener('hashchange', handleHash)
  }, [])

  const navigate = (page) => {
    window.location.hash = page
    setActivePage(page)
  }

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard': return <Dashboard apiBase={API_BASE} onNavigate={navigate} />
      case 'persona': return <PersonaBuilder apiBase={API_BASE} onNavigate={navigate} />
      case 'microsite': return <MicrositeBuilder apiBase={API_BASE} />
      case 'engagement': return <EngagementDashboard apiBase={API_BASE} />
      case 'triggers': return <TriggerPanel apiBase={API_BASE} />
      default: return <Dashboard apiBase={API_BASE} onNavigate={navigate} />
    }
  }

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-icon">🚀</div>
          <h1>SellSmart</h1>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              className={`nav-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => navigate(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
        <div style={{ padding: '0 24px', borderTop: '1px solid var(--border)', paddingTop: '16px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>SellSmart v1.0</div>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '4px' }}>AI-Powered Sales Intelligence</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  )
}
