import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import VoiceInterface from '../components/VoiceInterface'

export default function PersonaBuilder({ apiBase, onNavigate }) {
  const [mode, setMode] = useState('voice') // 'text' or 'voice'
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('idle') // idle | collecting | complete
  const [personaId, setPersonaId] = useState(null)
  const [persona, setPersona] = useState(null)
  const [propertyId, setPropertyId] = useState('')
  const [brokerId, setBrokerId] = useState('')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)

    try {
      const res = await fetch(`${apiBase}/api/v1/persona/text-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          broker_id: brokerId || null,
          property_id: propertyId || null,
          message: userMsg,
        }),
      })

      const data = await res.json()
      setSessionId(data.session_id)
      setStatus(data.session_status)
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])

      if (data.session_status === 'complete' && data.persona_id) {
        setPersonaId(data.persona_id)
        // Fetch the full persona
        const personaRes = await fetch(`${apiBase}/api/v1/persona/${data.persona_id}`)
        if (personaRes.ok) {
          setPersona(await personaRes.json())
        }
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Failed to connect. Make sure the API server is running on port 8000.',
      }])
    }
    setLoading(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const startNew = () => {
    setSessionId(null)
    setMessages([])
    setStatus('idle')
    setPersonaId(null)
    setPersona(null)
  }

  // If in voice mode, render VoiceInterface
  if (mode === 'voice') {
    return (
      <div>
        <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>🎙️ Persona Builder</h1>
            <p>Conversational AI-driven lead profiling — speak or type to build personas</p>
          </div>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => setMode('text')}
            style={{ whiteSpace: 'nowrap' }}
          >
            ⌨️ Switch to Text
          </button>
        </div>
        <VoiceInterface apiBase={apiBase} onNavigate={onNavigate} />
      </div>
    )
  }

  // Text mode UI
  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>🧠 Persona Builder</h1>
          <p>Conversational AI-driven lead profiling — describe your buyer and we'll build the persona</p>
        </div>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => setMode('voice')}
          style={{ whiteSpace: 'nowrap' }}
        >
          🎙️ Switch to Voice
        </button>
      </div>

      {/* Config Row */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', alignItems: 'flex-end' }}>
        <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
          <label>Property ID (optional)</label>
          <input
            className="input"
            placeholder="e.g. prop_dubai_creek"
            value={propertyId}
            onChange={e => setPropertyId(e.target.value)}
            disabled={status !== 'idle'}
          />
        </div>
        <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
          <label>Broker ID (optional)</label>
          <input
            className="input"
            placeholder="e.g. brk_5501"
            value={brokerId}
            onChange={e => setBrokerId(e.target.value)}
            disabled={status !== 'idle'}
          />
        </div>
        {status !== 'idle' && (
          <button className="btn btn-secondary btn-sm" onClick={startNew}>
            🔄 New Session
          </button>
        )}
        {status === 'complete' && (
          <button className="btn btn-primary btn-sm" onClick={() => onNavigate('microsite')}>
            🌐 Build Microsite
          </button>
        )}
      </div>

      {/* Status Badge */}
      <div style={{ marginBottom: '12px' }}>
        <span className={`badge ${status === 'complete' ? 'badge-success' :
          status === 'collecting' ? 'badge-warning' : 'badge-info'
          }`}>
          {status === 'complete' ? '✅ Persona Complete' :
            status === 'collecting' ? '🔄 Collecting Information' : '💬 Ready to Start'}
        </span>
        {sessionId && (
          <span style={{ fontSize: '12px', color: 'var(--text-dim)', marginLeft: '12px' }}>
            Session: {sessionId}
          </span>
        )}
      </div>

      {/* Chat Interface */}
      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
              <h3>Start the conversation</h3>
              <p style={{ fontSize: '14px', marginTop: '8px' }}>
                Tell the AI about your buyer — their nationality, interests, budget, motivation...
              </p>
              <p style={{ fontSize: '13px', marginTop: '12px', color: 'var(--text-dim)' }}>
                Example: "I have an Indian investor looking for a 2-bed in Dubai for Golden Visa eligibility"
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role}`}>
              <div className="sender">
                {msg.role === 'user' ? 'You (Broker)' : 'SellSmart AI'}
              </div>
              {msg.role === 'assistant' ? (
                <div className="markdown-content">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                msg.content
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble assistant">
              <div className="sender">SellSmart AI</div>
              <span className="loading-dots">Thinking</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-bar">
          <input
            className="input"
            placeholder={status === 'complete' ? 'Persona complete! Click "Build Microsite" to continue.' : 'Describe your buyer...'}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading || status === 'complete'}
          />
          <button
            className="btn btn-primary"
            onClick={sendMessage}
            disabled={loading || !input.trim() || status === 'complete'}
          >
            {loading ? <div className="spinner" /> : 'Send'}
          </button>
        </div>
      </div>

      {/* Persona Preview */}
      {persona && (
        <div className="persona-preview">
          <div className="persona-header">
            <div className="persona-avatar">👤</div>
            <div>
              <h2>{persona.ai_recommended_persona_type || 'Buyer'} Persona</h2>
              <span style={{ fontSize: '13px', color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                {persona.persona_id}
              </span>
              {persona.ai_persona_label && (
                <div style={{ fontSize: '13px', color: 'var(--primary-light)', marginTop: '4px' }}>
                  {persona.ai_persona_label}
                </div>
              )}
            </div>
            <div style={{ marginLeft: 'auto' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '24px', fontWeight: '700' }}>{persona.trust_level_score}</div>
                <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>Trust Score</div>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div className="persona-field">
              <div className="field-label">Primary Motivation</div>
              <div className="field-value">{persona.motivation?.primary_goal || '—'}</div>
            </div>
            <div className="persona-field">
              <div className="field-label">Nationality</div>
              <div className="field-value">{persona.identity?.nationality || '—'}</div>
            </div>
            <div className="persona-field">
              <div className="field-label">Budget</div>
              <div className="field-value">
                {persona.financial?.budget_min || persona.financial?.budget_max
                  ? `${persona.financial.budget_min?.toLocaleString() || '—'} – ${persona.financial.budget_max?.toLocaleString() || '—'} AED`
                  : '—'}
              </div>
            </div>
            <div className="persona-field">
              <div className="field-label">Urgency</div>
              <div className="field-value">{persona.motivation?.urgency || '—'}</div>
            </div>
            <div className="persona-field">
              <div className="field-label">Lifestyle & Interests</div>
              <div className="field-value">
                {(persona.lifestyle?.lifestyle_tags || []).length > 0
                  ? persona.lifestyle.lifestyle_tags.map((k, i) => (
                    <span key={i} className="badge badge-primary" style={{ marginRight: '4px', marginBottom: '4px' }}>
                      {k}
                    </span>
                  ))
                  : '—'}
              </div>
            </div>
            <div className="persona-field">
              <div className="field-label">Deal Breakers</div>
              <div className="field-value">
                {(persona.lifestyle?.deal_breaker_features || []).length > 0
                  ? persona.lifestyle.deal_breaker_features.map((k, i) => (
                    <span key={i} className="badge badge-danger" style={{ marginRight: '4px', marginBottom: '4px' }}>
                      {k}
                    </span>
                  ))
                  : '—'}
              </div>
            </div>
            <div className="persona-field">
              <div className="field-label">Property Type</div>
              <div className="field-value">{persona.property_fit?.unit_type || '—'}</div>
            </div>
            <div className="persona-field">
              <div className="field-label">View Preference</div>
              <div className="field-value">{persona.property_fit?.view_preference || '—'}</div>
            </div>
          </div>

          {persona.ai_recommended_angle && (
            <div className="persona-field" style={{ marginTop: '12px' }}>
              <div className="field-label">AI Recommended Sales Angle</div>
              <div className="field-value" style={{
                padding: '12px',
                background: 'var(--bg)',
                borderRadius: 'var(--radius-sm)',
                borderLeft: '3px solid var(--primary)',
              }}>
                💡 {persona.ai_recommended_angle}
              </div>
            </div>
          )}

          {persona.next_best_action && (
            <div className="persona-field" style={{ marginTop: '8px' }}>
              <div className="field-label">Next Best Action</div>
              <div className="field-value">{persona.next_best_action}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
