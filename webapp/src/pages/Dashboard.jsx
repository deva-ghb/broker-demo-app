import { useState, useEffect } from 'react'

export default function Dashboard({ apiBase, onNavigate }) {
  const [personas, setPersonas] = useState([])
  const [triggers, setTriggers] = useState([])
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [healthRes, personaRes, triggerRes] = await Promise.allSettled([
        fetch(`${apiBase}/health`).then(r => r.json()),
        fetch(`${apiBase}/api/v1/persona/`).then(r => r.json()),
        fetch(`${apiBase}/api/v1/triggers/get`).then(r => r.json()),
      ])
      if (healthRes.status === 'fulfilled') setHealth(healthRes.value)
      if (personaRes.status === 'fulfilled') setPersonas(personaRes.value.personas || [])
      if (triggerRes.status === 'fulfilled') setTriggers(triggerRes.value.triggers || [])
    } catch (e) {
      console.error('Failed to fetch dashboard data', e)
    }
    setLoading(false)
  }

  const activeLeads = personas.filter(p => p.session_status === 'complete').length
  const activeTriggers = triggers.filter(t => !t.is_read).length

  return (
    <div>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your sales pipeline and AI insights</p>
      </div>

      {/* System Status */}
      {health && (
        <div style={{ marginBottom: '24px', display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className={`badge ${health.status === 'ok' ? 'badge-success' : 'badge-warning'}`}>
            {health.status === 'ok' ? '● System Online' : '⚠ Degraded'}
          </span>
          <span className={`badge ${health.db === 'connected' ? 'badge-success' : 'badge-danger'}`}>
            DB: {health.db}
          </span>
          <span className={`badge ${health.qdrant === 'connected' ? 'badge-success' : 'badge-danger'}`}>
            Qdrant: {health.qdrant}
          </span>
        </div>
      )}

      {/* Stats */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon">👤</div>
          <div className="stat-value">{personas.length}</div>
          <div className="stat-label">Total Personas</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-value">{activeLeads}</div>
          <div className="stat-label">Active Leads</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🔔</div>
          <div className="stat-value">{activeTriggers}</div>
          <div className="stat-label">Active Triggers</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🌐</div>
          <div className="stat-value">—</div>
          <div className="stat-label">Active Microsites</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ marginBottom: '12px' }}>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-primary" onClick={() => onNavigate('persona')}>
            🧠 New Persona
          </button>
          <button className="btn btn-secondary" onClick={() => onNavigate('triggers')}>
            🔔 View Triggers ({activeTriggers})
          </button>
          <button className="btn btn-secondary" onClick={fetchData}>
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Recent Personas */}
      <div className="card" style={{ marginBottom: '16px' }}>
        <h2 style={{ marginBottom: '16px' }}>Recent Personas</h2>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '20px' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>
        ) : personas.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🧠</div>
            <h3>No personas yet</h3>
            <p>Start a conversation to build your first buyer persona.</p>
            <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={() => onNavigate('persona')}>
              Create Persona
            </button>
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Persona ID</th>
                <th>Type</th>
                <th>Motivation</th>
                <th>Trust Score</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {personas.slice(0, 10).map(p => (
                <tr key={p.persona_id}>
                  <td style={{ fontFamily: 'monospace', fontSize: '13px' }}>{p.persona_id}</td>
                  <td><span className="badge badge-primary">{p.ai_recommended_persona_type || '—'}</span></td>
                  <td>{p.motivation?.primary_goal || '—'}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div className="progress-bar" style={{ width: '80px' }}>
                        <div className="progress-fill" style={{ width: `${p.trust_level_score}%` }} />
                      </div>
                      <span style={{ fontSize: '13px' }}>{p.trust_level_score}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${p.session_status === 'complete' ? 'badge-success' : 'badge-warning'}`}>
                      {p.session_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Recent Triggers */}
      {triggers.length > 0 && (
        <div className="card">
          <h2 style={{ marginBottom: '16px' }}>🔔 Latest Triggers</h2>
          {triggers.slice(0, 5).map(t => (
            <div key={t.trigger_id} className={`trigger-card ${t.trigger_type}`}>
              <div className="trigger-header">
                <span className={`badge ${t.trigger_type === 'high_intent' ? 'badge-danger' :
                  t.trigger_type === 'specific_interest' ? 'badge-warning' : 'badge-success'
                  }`}>
                  {t.trigger_type.replace('_', ' ')}
                </span>
                <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>{t.timing}</span>
              </div>
              <p className="trigger-message">{t.message}</p>
              {t.talking_point && (
                <p className="trigger-talking-point">💬 "{t.talking_point}"</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
