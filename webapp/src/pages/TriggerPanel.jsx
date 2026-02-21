import { useState, useEffect, useRef } from 'react'

export default function TriggerPanel({ apiBase }) {
  const [triggers, setTriggers] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all | high_intent | specific_interest | completion
  const [wsConnected, setWsConnected] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    fetchTriggers()
    connectWebSocket()
    return () => {
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  const fetchTriggers = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${apiBase}/api/v1/triggers/get`)
      const data = await res.json()
      setTriggers(data.triggers || [])
    } catch (e) {
      console.error('Failed to fetch triggers', e)
    }
    setLoading(false)
  }

  const connectWebSocket = () => {
    try {
      const wsUrl = apiBase.replace('http', 'ws') + '/api/v1/triggers/stream'
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => setWsConnected(true)
      ws.onclose = () => {
        setWsConnected(false)
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000)
      }
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'new_triggers') {
          setTriggers(prev => [...data.triggers, ...prev])
        }
      }
      ws.onerror = () => setWsConnected(false)
    } catch (e) {
      console.error('WebSocket error', e)
    }
  }

  const markRead = async (triggerId) => {
    try {
      await fetch(`${apiBase}/api/v1/triggers/${triggerId}/read`, { method: 'POST' })
      setTriggers(prev => prev.map(t =>
        t.trigger_id === triggerId ? { ...t, is_read: true } : t
      ))
    } catch (e) {
      console.error('Failed to mark read', e)
    }
  }

  const filtered = triggers.filter(t =>
    filter === 'all' ? true : t.trigger_type === filter
  )

  const unreadCount = triggers.filter(t => !t.is_read).length

  return (
    <div>
      <div className="page-header">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1>🔔 Trigger Panel</h1>
            <p>AI-generated follow-up alerts based on buyer engagement</p>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span className={`badge ${wsConnected ? 'badge-success' : 'badge-danger'}`}>
              {wsConnected ? '● Live' : '○ Offline'}
            </span>
            <button className="btn btn-secondary btn-sm" onClick={fetchTriggers}>
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-row">
        <div className="stat-card" onClick={() => setFilter('all')} style={{ cursor: 'pointer', borderColor: filter === 'all' ? 'var(--primary)' : undefined }}>
          <div className="stat-icon">📋</div>
          <div className="stat-value">{triggers.length}</div>
          <div className="stat-label">Total Triggers</div>
        </div>
        <div className="stat-card" onClick={() => setFilter('high_intent')} style={{ cursor: 'pointer', borderColor: filter === 'high_intent' ? 'var(--danger)' : undefined }}>
          <div className="stat-icon">🔥</div>
          <div className="stat-value">{triggers.filter(t => t.trigger_type === 'high_intent').length}</div>
          <div className="stat-label">Hot Leads</div>
        </div>
        <div className="stat-card" onClick={() => setFilter('specific_interest')} style={{ cursor: 'pointer', borderColor: filter === 'specific_interest' ? 'var(--warning)' : undefined }}>
          <div className="stat-icon">📊</div>
          <div className="stat-value">{triggers.filter(t => t.trigger_type === 'specific_interest').length}</div>
          <div className="stat-label">Interest Signals</div>
        </div>
        <div className="stat-card" onClick={() => setFilter('completion')} style={{ cursor: 'pointer', borderColor: filter === 'completion' ? 'var(--success)' : undefined }}>
          <div className="stat-icon">✅</div>
          <div className="stat-value">{triggers.filter(t => t.trigger_type === 'completion').length}</div>
          <div className="stat-label">Completions</div>
        </div>
      </div>

      {/* Unread Banner */}
      {unreadCount > 0 && (
        <div style={{
          padding: '12px 16px',
          background: 'var(--primary-bg)',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <span style={{ color: 'var(--primary-light)', fontWeight: 500 }}>
            🔔 {unreadCount} unread trigger{unreadCount > 1 ? 's' : ''}
          </span>
        </div>
      )}

      {/* Triggers List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}><div className="spinner" style={{ margin: '0 auto' }} /></div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔔</div>
          <h3>No triggers yet</h3>
          <p>Triggers will appear when buyers interact with your microsites.</p>
        </div>
      ) : (
        filtered.map(t => (
          <div
            key={t.trigger_id}
            className={`trigger-card ${t.trigger_type}`}
            style={{ opacity: t.is_read ? 0.6 : 1 }}
          >
            <div className="trigger-header">
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span className={`badge ${
                  t.trigger_type === 'high_intent' ? 'badge-danger' :
                  t.trigger_type === 'specific_interest' ? 'badge-warning' : 'badge-success'
                }`}>
                  {t.trigger_type === 'high_intent' ? '🔥 Hot Lead' :
                   t.trigger_type === 'specific_interest' ? '📊 Interest' : '✅ Complete'}
                </span>
                <span className="badge badge-info">{t.timing}</span>
                {!t.is_read && <span className="badge badge-primary">NEW</span>}
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                  Confidence: {Math.round(t.confidence_score * 100)}%
                </span>
                {!t.is_read && (
                  <button className="btn btn-secondary btn-sm" onClick={() => markRead(t.trigger_id)}>
                    ✓ Read
                  </button>
                )}
              </div>
            </div>

            <p className="trigger-message">{t.message}</p>

            {t.talking_point && (
              <p className="trigger-talking-point">
                💬 <strong>Talking Point:</strong> "{t.talking_point}"
              </p>
            )}

            <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--text-dim)' }}>
              Lead: <span style={{ fontFamily: 'monospace' }}>{t.persona_id}</span>
              {t.created_at && (
                <> · {new Date(t.created_at).toLocaleString()}</>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
