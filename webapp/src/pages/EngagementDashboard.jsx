import { useState, useEffect } from 'react'

export default function EngagementDashboard({ apiBase }) {
  const [trackingId, setTrackingId] = useState('')
  const [summary, setSummary] = useState(null)
  const [personas, setPersonas] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchPersonas()
  }, [])

  const fetchPersonas = async () => {
    try {
      const res = await fetch(`${apiBase}/api/v1/persona/`)
      const data = await res.json()
      setPersonas((data.personas || []).filter(p => p.session_status === 'complete'))
    } catch (e) {
      console.error('Failed to fetch personas', e)
    }
  }

  const fetchSummary = async (id) => {
    const target = id || trackingId
    if (!target) return
    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${apiBase}/api/v1/engagement/${target}/summary`)
      if (!res.ok) throw new Error('Not found')
      setSummary(await res.json())
    } catch (e) {
      setError('No engagement data found for this ID')
      setSummary(null)
    }
    setLoading(false)
  }

  const maxDwell = summary?.section_dwell_times
    ? Math.max(...Object.values(summary.section_dwell_times), 1)
    : 1

  return (
    <div>
      <div className="page-header">
        <h1>📈 Engagement Dashboard</h1>
        <p>Track how buyers interact with your microsites</p>
      </div>

      {/* Search */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
            <label>Select Lead or Enter Tracking ID</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <select
                className="input select"
                value={trackingId}
                onChange={e => { setTrackingId(e.target.value); if (e.target.value) fetchSummary(e.target.value); }}
                style={{ flex: 1 }}
              >
                <option value="">— Select a persona —</option>
                {personas.map(p => (
                  <option key={p.persona_id} value={p.persona_id}>
                    {p.persona_id} — {p.persona_type || 'Unknown'}
                  </option>
                ))}
              </select>
              <input
                className="input"
                placeholder="or enter tracking_id"
                value={trackingId}
                onChange={e => setTrackingId(e.target.value)}
                style={{ flex: 1 }}
              />
              <button className="btn btn-primary" onClick={() => fetchSummary()} disabled={!trackingId || loading}>
                {loading ? <div className="spinner" /> : '🔍 Fetch'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="card" style={{ marginBottom: '16px', borderColor: 'var(--warning)' }}>
          <p style={{ color: 'var(--warning)' }}>⚠️ {error}</p>
        </div>
      )}

      {summary && (
        <>
          {/* Stats */}
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-icon">👁️</div>
              <div className="stat-value">{summary.total_page_views}</div>
              <div className="stat-label">Page Views</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🔄</div>
              <div className="stat-value">{summary.return_visit_count}</div>
              <div className="stat-label">Return Visits</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📜</div>
              <div className="stat-value">{summary.max_scroll_depth}%</div>
              <div className="stat-label">Max Scroll Depth</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🖱️</div>
              <div className="stat-value">{summary.cta_clicks || 0}</div>
              <div className="stat-label">CTA Clicks</div>
            </div>
          </div>

          {/* Scroll Depth Visual */}
          <div className="card" style={{ marginBottom: '16px' }}>
            <h2 style={{ marginBottom: '16px' }}>📜 Scroll Depth</h2>
            <div className="progress-bar" style={{ height: '12px' }}>
              <div
                className="progress-fill"
                style={{
                  width: `${summary.max_scroll_depth}%`,
                  background: summary.max_scroll_depth >= 100
                    ? 'linear-gradient(90deg, var(--success), #34d399)'
                    : undefined,
                }}
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px', fontSize: '12px', color: 'var(--text-dim)' }}>
              <span>0%</span>
              <span>25%</span>
              <span>50%</span>
              <span>75%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Section Dwell Times */}
          <div className="card" style={{ marginBottom: '16px' }}>
            <h2 style={{ marginBottom: '16px' }}>⏱️ Section Dwell Times</h2>
            {Object.keys(summary.section_dwell_times || {}).length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>No dwell time data yet</p>
            ) : (
              <div>
                {Object.entries(summary.section_dwell_times)
                  .sort(([, a], [, b]) => b - a)
                  .map(([section, seconds]) => (
                    <div key={section} style={{ marginBottom: '12px' }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        marginBottom: '4px',
                        fontSize: '13px',
                      }}>
                        <span>{section.replace(/_/g, ' ')}</span>
                        <span style={{ color: 'var(--text-muted)' }}>
                          {seconds >= 60 ? `${(seconds / 60).toFixed(1)} min` : `${seconds.toFixed(1)}s`}
                        </span>
                      </div>
                      <div className="progress-bar">
                        <div
                          className="progress-fill"
                          style={{
                            width: `${(seconds / maxDwell) * 100}%`,
                            background: summary.high_dwell_sections?.includes(section)
                              ? 'linear-gradient(90deg, var(--warning), #fbbf24)'
                              : undefined,
                          }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>

          {/* High Dwell Sections */}
          {summary.high_dwell_sections?.length > 0 && (
            <div className="card">
              <h2 style={{ marginBottom: '12px' }}>🔥 High Interest Sections</h2>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {summary.high_dwell_sections.map((s, i) => (
                  <span key={i} className="badge badge-warning">
                    {s.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {!summary && !error && (
        <div className="empty-state">
          <div className="empty-icon">📈</div>
          <h3>Select a lead to view engagement data</h3>
          <p>Choose a persona from the dropdown above or enter a tracking ID.</p>
        </div>
      )}
    </div>
  )
}
