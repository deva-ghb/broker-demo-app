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

  const selectedPersonaDetails = personas.find(p => p.persona_id === selectedPersona)

  return (
    <div>
      <div className="page-header">
        <h1>Microsite Builder</h1>
        <p>Generate personalized, AI-curated property microsites for your leads</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Build Form */}
        <div className="card">
          <h2 style={{ marginBottom: '24px', fontSize: '14px', letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>
            Build Configuration
          </h2>

          <div className="form-group">
            <label>Buyer Persona</label>
            <select
              className="input select"
              value={selectedPersona}
              onChange={e => setSelectedPersona(e.target.value)}
            >
              <option value="">Select a completed persona</option>
              {personas.map(p => (
                <option key={p.persona_id} value={p.persona_id}>
                  {p.ai_recommended_persona_type || 'Unknown'} — {p.motivation?.primary_goal || p.persona_id}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Property</label>
            <select
              className="input select"
              value={propertyId}
              onChange={e => setPropertyId(e.target.value)}
            >
              <option value="">Auto-Select via AI Recommendation</option>
              {properties.map(p => (
                <option key={p.property_id} value={p.property_id}>
                  {p.name}
                </option>
              ))}
            </select>
            <span style={{ fontSize: '11px', color: 'var(--text-dim)', marginTop: '6px', display: 'block', lineHeight: 1.5 }}>
              Leave unselected to let the AI match the best property using vector similarity.
            </span>
          </div>

          <button
            className="btn btn-primary"
            onClick={buildMicrosite}
            disabled={loading || !selectedPersona}
            style={{ width: '100%', justifyContent: 'center', marginTop: '4px' }}
          >
            {loading ? (
              <><div className="spinner" /> Generating...</>
            ) : (
              'Generate Microsite'
            )}
          </button>

          {error && (
            <div style={{
              marginTop: '14px',
              padding: '12px 16px',
              background: 'rgba(239, 68, 68, 0.08)',
              borderRadius: 'var(--radius-xs)',
              border: '1px solid rgba(239,68,68,0.2)',
              color: 'var(--danger)',
              fontSize: '13px',
              lineHeight: 1.6,
            }}>
              {error}
            </div>
          )}
        </div>

        {/* Result Panel */}
        <div className="card">
          <h2 style={{ marginBottom: '24px', fontSize: '14px', letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>
            Generated Microsite
          </h2>

          {result ? (
            <div>
              <div style={{
                padding: '24px',
                background: 'rgba(204,152,65,0.06)',
                border: '1px solid rgba(204,152,65,0.18)',
                borderRadius: 'var(--radius)',
                marginBottom: '20px',
                textAlign: 'center',
              }}>
                <div style={{
                  width: 40, height: 40,
                  background: 'var(--gold)',
                  borderRadius: 12,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  margin: '0 auto 12px',
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="2.5">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
                <div style={{ fontFamily: 'Instrument Sans', fontSize: '16px', fontWeight: 500, color: 'var(--text)', marginBottom: '4px' }}>
                  Microsite Ready
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
                  AI-personalized and tracking-enabled
                </div>
              </div>

              <div className="persona-field">
                <div className="field-label">Microsite URL</div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <input
                    className="input"
                    value={result.microsite_url}
                    readOnly
                    style={{ flex: 1, fontFamily: 'monospace', fontSize: '12px' }}
                  />
                  <button className="btn btn-secondary btn-sm" onClick={copyUrl}>Copy</button>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '14px' }}>
                <div className="persona-field">
                  <div className="field-label">Tracking ID</div>
                  <div className="field-value" style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                    {result.tracking_id}
                  </div>
                </div>
                <div className="persona-field">
                  <div className="field-label">Microsite ID</div>
                  <div className="field-value" style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                    {result.microsite_id}
                  </div>
                </div>
              </div>

              <div style={{ marginTop: '20px' }}>
                <a
                  href={`${result.microsite_url}?preview=true`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary"
                  style={{ textDecoration: 'none', width: '100%', justifyContent: 'center' }}
                >
                  Open Microsite
                </a>
              </div>
            </div>
          ) : (
            <div className="empty-state" style={{ padding: '40px 20px' }}>
              <div style={{
                width: 48, height: 48,
                border: '1px solid var(--border-card)',
                borderRadius: 14,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 16px',
                background: 'rgba(255,255,255,0.02)',
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-dim)" strokeWidth="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>
                </svg>
              </div>
              <h3>No microsite generated yet</h3>
              <p>Select a persona and click Generate to build a personalized microsite.</p>
            </div>
          )}
        </div>
      </div>

      {/* Selected Persona Details */}
      {selectedPersonaDetails && (
        <div className="card" style={{ marginTop: '16px' }}>
          <h2 style={{ marginBottom: '16px', fontSize: '14px', letterSpacing: '0.04em', textTransform: 'uppercase', color: 'var(--text-dim)' }}>
            Persona Context
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div className="persona-field">
              <div className="field-label">Type</div>
              <div className="field-value">
                <span className="badge badge-primary">{selectedPersonaDetails.ai_recommended_persona_type || '—'}</span>
              </div>
            </div>
            <div className="persona-field">
              <div className="field-label">Primary Goal</div>
              <div className="field-value">{selectedPersonaDetails.motivation?.primary_goal || '—'}</div>
            </div>
            <div className="persona-field">
              <div className="field-label">Trust Score</div>
              <div className="field-value" style={{ fontFamily: 'Instrument Sans', fontSize: '18px', fontWeight: 600 }}>
                {selectedPersonaDetails.trust_level_score}
              </div>
            </div>
            <div className="persona-field" style={{ gridColumn: 'span 3' }}>
              <div className="field-label">Lifestyle</div>
              <div className="field-value">
                {(selectedPersonaDetails.lifestyle?.lifestyle_tags || []).length > 0
                  ? selectedPersonaDetails.lifestyle.lifestyle_tags.map((k, i) => (
                    <span key={i} className="badge badge-primary" style={{ marginRight: '4px', marginBottom: '4px' }}>{k}</span>
                  ))
                  : '—'}
              </div>
            </div>
          </div>
          {selectedPersonaDetails.ai_recommended_angle && (
            <div className="persona-field" style={{ marginTop: '12px' }}>
              <div className="field-label">AI Sales Angle</div>
              <div className="gold-block">{selectedPersonaDetails.ai_recommended_angle}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
