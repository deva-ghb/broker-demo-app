import { useState, useEffect } from 'react'

export default function MicrositeBuilder({ apiBase }) {
  const [personas, setPersonas] = useState([])
  const [properties, setProperties] = useState([])
  const [selectedPersona, setSelectedPersona] = useState('')
  const [propertyId, setPropertyId] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchPersonas()
    fetchProperties()
  }, [])

  const fetchProperties = async () => {
    try {
      const res = await fetch(`${apiBase}/api/v1/properties/`)
      const data = await res.json()
      setProperties(data.properties || [])
    } catch (e) {
      console.error('Failed to fetch properties', e)
    }
  }

  const fetchPersonas = async () => {
    try {
      const res = await fetch(`${apiBase}/api/v1/persona/`)
      const data = await res.json()
      setPersonas((data.personas || []).filter(p => p.session_status === 'complete'))
    } catch (e) {
      console.error('Failed to fetch personas', e)
    }
  }

  const buildMicrosite = async () => {
    if (!selectedPersona) return
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${apiBase}/api/v1/microsite/build`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          persona_id: selectedPersona,
          property_id: propertyId || null,
        }),
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Build failed')
      }

      setResult(await res.json())
    } catch (e) {
      setError(e.message)
    }
    setLoading(false)
  }

  const copyUrl = () => {
    if (result?.microsite_url) {
      navigator.clipboard.writeText(result.microsite_url)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>🌐 Microsite Builder</h1>
        <p>Generate personalized, trackable property microsites for your leads</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Build Form */}
        <div className="card">
          <h2 style={{ marginBottom: '20px' }}>Build Configuration</h2>

          <div className="form-group">
            <label>Select Persona</label>
            <select
              className="input select"
              value={selectedPersona}
              onChange={e => setSelectedPersona(e.target.value)}
            >
              <option value="">— Choose a completed persona —</option>
              {personas.map(p => (
                <option key={p.persona_id} value={p.persona_id}>
                  {p.persona_id} — {p.persona_type || 'Unknown'} ({p.primary_motivation || '—'})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Property Selection</label>
            <select
              className="input select"
              value={propertyId}
              onChange={e => setPropertyId(e.target.value)}
            >
              <option value="">✨ Auto-Select (AI Recommendation)</option>
              {properties.map(p => (
                <option key={p.property_id} value={p.property_id}>
                  {p.name} ({p.property_id})
                </option>
              ))}
            </select>
            <span style={{ fontSize: '12px', color: 'var(--text-dim)', marginTop: '4px', display: 'block' }}>
              Leave on Auto-Select to let the AI natively match the best property for the persona.
            </span>
          </div>

          <button
            className="btn btn-primary"
            onClick={buildMicrosite}
            disabled={loading || !selectedPersona}
            style={{ width: '100%', justifyContent: 'center' }}
          >
            {loading ? (
              <><div className="spinner" /> Generating...</>
            ) : (
              '🚀 Generate Microsite'
            )}
          </button>

          {error && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              background: 'rgba(239, 68, 68, 0.1)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--danger)',
              fontSize: '14px',
            }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Result */}
        <div className="card">
          <h2 style={{ marginBottom: '20px' }}>Generated Microsite</h2>

          {result ? (
            <div>
              <div style={{
                padding: '20px',
                background: 'var(--bg)',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '16px',
                textAlign: 'center',
              }}>
                <div style={{ fontSize: '48px', marginBottom: '12px' }}>✅</div>
                <h3>Microsite Ready!</h3>
              </div>

              <div className="persona-field">
                <div className="field-label">Microsite URL</div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <input className="input" value={result.microsite_url} readOnly style={{ flex: 1, fontFamily: 'monospace' }} />
                  <button className="btn btn-secondary btn-sm" onClick={copyUrl}>📋 Copy</button>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px' }}>
                <div className="persona-field">
                  <div className="field-label">Tracking ID</div>
                  <div className="field-value" style={{ fontFamily: 'monospace', fontSize: '13px' }}>
                    {result.tracking_id}
                  </div>
                </div>
                <div className="persona-field">
                  <div className="field-label">Microsite ID</div>
                  <div className="field-value" style={{ fontFamily: 'monospace', fontSize: '13px' }}>
                    {result.microsite_id}
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
                <a
                  href={result.microsite_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                  style={{ textDecoration: 'none', flex: 1, justifyContent: 'center' }}
                >
                  🔗 Open Microsite
                </a>
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">🌐</div>
              <h3>No microsite generated yet</h3>
              <p>Select a persona and property, then click Generate.</p>
            </div>
          )}
        </div>
      </div>

      {/* Selected Persona Preview */}
      {selectedPersona && personas.find(p => p.persona_id === selectedPersona) && (() => {
        const p = personas.find(p => p.persona_id === selectedPersona)
        return (
          <div className="card" style={{ marginTop: '16px' }}>
            <h2 style={{ marginBottom: '12px' }}>📋 Selected Persona Details</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              <div className="persona-field">
                <div className="field-label">Type</div>
                <div className="field-value">
                  <span className="badge badge-primary">{p.persona_type || '—'}</span>
                </div>
              </div>
              <div className="persona-field">
                <div className="field-label">Motivation</div>
                <div className="field-value">{p.primary_motivation || '—'}</div>
              </div>
              <div className="persona-field">
                <div className="field-label">Trust Score</div>
                <div className="field-value">{p.trust_level_score}</div>
              </div>
              <div className="persona-field" style={{ gridColumn: 'span 2' }}>
                <div className="field-label">Key Interests</div>
                <div className="field-value">
                  {(p.key_interests || []).map((k, i) => (
                    <span key={i} className="badge badge-primary" style={{ marginRight: '4px' }}>{k}</span>
                  ))}
                </div>
              </div>
              <div className="persona-field">
                <div className="field-label">Ignored Features</div>
                <div className="field-value">
                  {(p.ignored_features || []).map((k, i) => (
                    <span key={i} className="badge badge-danger" style={{ marginRight: '4px' }}>{k}</span>
                  ))}
                </div>
              </div>
            </div>
            {p.ai_recommended_angle && (
              <div className="persona-field" style={{ marginTop: '12px' }}>
                <div className="field-label">AI Sales Angle</div>
                <div className="field-value" style={{
                  padding: '10px',
                  background: 'var(--bg)',
                  borderRadius: 'var(--radius-sm)',
                  borderLeft: '3px solid var(--primary)',
                }}>
                  💡 {p.ai_recommended_angle}
                </div>
              </div>
            )}
          </div>
        )
      })()}
    </div>
  )
}
