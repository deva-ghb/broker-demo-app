import { useState, useEffect } from 'react'
import './index.css'
import Dashboard from './pages/Dashboard'
import PersonaBuilder from './pages/PersonaBuilder'
import MicrositeBuilder from './pages/MicrositeBuilder'
import EngagementDashboard from './pages/EngagementDashboard'
import TriggerPanel from './pages/TriggerPanel'

const API_BASE = 'http://localhost:8000'

const NAV_ITEMS = [
  { id: 'dashboard',   label: 'Dashboard' },
  { id: 'persona',     label: 'Persona Builder' },
  { id: 'microsite',   label: 'Microsite Builder' },
  { id: 'engagement',  label: 'Engagement' },
  { id: 'triggers',    label: 'Triggers' },
]

export default function App() {
  const [activePage, setActivePage] = useState('dashboard')

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
      case 'dashboard':  return <Dashboard apiBase={API_BASE} onNavigate={navigate} />
      case 'persona':    return <PersonaBuilder apiBase={API_BASE} onNavigate={navigate} />
      case 'microsite':  return <MicrositeBuilder apiBase={API_BASE} />
      case 'engagement': return <EngagementDashboard apiBase={API_BASE} />
      case 'triggers':   return <TriggerPanel apiBase={API_BASE} />
      default:           return <Dashboard apiBase={API_BASE} onNavigate={navigate} />
    }
  }

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-mark">
            {/* Gold diamond mark */}
            <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 1L17 6.5V11.5L9 17L1 11.5V6.5L9 1Z" fill="#000" fillOpacity="0.9"/>
            </svg>
          </div>
          <div>
            <h1>SellSmart</h1>
            <div className="logo-sub">AI Sales Intelligence</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              className={`nav-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => navigate(item.id)}
            >
              <span className="nav-dot" />
              {item.label}
            </button>
          ))}
        </nav>

        <div style={{ padding: '0 24px', borderTop: '1px solid var(--border-card)', paddingTop: '16px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-dim)', letterSpacing: '0.03em' }}>v1.0 · Treppan Group</div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  )
}
