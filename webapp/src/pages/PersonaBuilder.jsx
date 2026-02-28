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
        const personaRes = await fetch(`${apiBase}/api/v1/persona/${data.persona_id}`)
        if (personaRes.ok) {
          setPersona(await personaRes.json())
        }
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Failed to connect. Please ensure the API server is running.',
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

  if (mode === 'voice') {
    return (
      <div>
        <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>Persona Builder</h1>
            <p>Conversational AI-driven lead profiling — speak or type to build buyer personas</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => setMode('text')}>
            Switch to Text
          </button>
        </div>
        <VoiceInterface apiBase={apiBase} onNavigate={onNavigate} />
      </div>
    )
  }

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1>Persona Builder</h1>
          <p>Describe your buyer and SellSmart AI will build a structured intelligence profile</p>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => setMode('voice')}>
          Switch to Voice
        </button>
      </div>

      {/* Config Row */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', alignItems: 'flex-end' }}>
        <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
          <label>Property Context (optional)</label>
          <input
            className="input"
            placeholder="Property ID"
            value={propertyId}
            onChange={e => setPropertyId(e.target.value)}
            disabled={status !== 'idle'}
          />
        </div>
        <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
          <label>Broker ID (optional)</label>
          <input
            className="input"
            placeholder="Broker ID"
            value={brokerId}
            onChange={e => setBrokerId(e.target.value)}
            disabled={status !== 'idle'}
          />
        </div>
        {status !== 'idle' && (
          <button className="btn btn-secondary btn-sm" onClick={startNew}>
            New Session
          </button>
        )}
        {status === 'complete' && (
          <button className="btn btn-primary btn-sm" onClick={() => onNavigate('microsite')}>
            Build Microsite
          </button>
        )}
      </div>

      {/* Status Badge */}
      <div style={{ marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span className={`badge ${status === 'complete' ? 'badge-success' :
          status === 'collecting' ? 'badge-warning' : 'badge-info'}`}>
          {status === 'complete' ? 'Persona Complete' :
            status === 'collecting' ? 'Collecting Information' : 'Ready to Start'}
        </span>
        {sessionId && (
          <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: 'monospace' }}>
            {sessionId}
          </span>
        )}
      </div>

      {/* Chat Interface */}
      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-dim)' }}>
              <div style={{
                width: 48, height: 48, margin: '0 auto 20px',
                border: '1px solid var(--border-card)',
                borderRadius: 14,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'rgba(204,152,65,0.08)'
              }}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" strokeWidth="1.5">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <h3 style={{ marginBottom: '8px', fontSize: '15px' }}>Begin the conversation</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-dim)', maxWidth: '300px', margin: '0 auto', lineHeight: 1.7 }}>
                Describe your buyer — nationality, budget, motivation, lifestyle preferences
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role}`}>
              <div className="sender">
                {msg.role === 'user' ? 'Broker' : 'SellSmart AI'}
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
            placeholder={status === 'complete' ? 'Persona complete — build a microsite to continue' : 'Describe your buyer...'}
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
            <div className="persona-avatar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--gold)" strokeWidth="1.5">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
            <div>
              <h2 style={{ fontFamily: 'Instrument Sans', fontSize: '15px' }}>
                {persona.ai_recommended_persona_type || 'Buyer'} Persona
              </h2>
              <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontFamily: 'monospace' }}>
                {persona.persona_id}
              </span>
              {persona.ai_persona_label && (
                <div style={{ fontSize: '12px', color: 'var(--gold)', marginTop: '3px' }}>
                  {persona.ai_persona_label}
                </div>
              )}
            </div>
            <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
              <div style={{ fontFamily: 'Instrument Sans', fontSize: '28px', fontWeight: 600, color: 'var(--text)' }}>
                {persona.trust_level_score}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-dim)', letterSpacing: '0.06em', textTransform: 'uppercase' }}>Trust Score</div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
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
              <div className="field-label">Lifestyle</div>
              <div className="field-value">
                {(persona.lifestyle?.lifestyle_tags || []).length > 0
                  ? persona.lifestyle.lifestyle_tags.map((k, i) => (
                    <span key={i} className="badge badge-primary" style={{ marginRight: '4px', marginBottom: '4px' }}>{k}</span>
                  ))
                  : '—'}
              </div>
            </div>
            <div className="persona-field">
              <div className="field-label">Deal Breakers</div>
              <div className="field-value">
                {(persona.lifestyle?.deal_breaker_features || []).length > 0
                  ? persona.lifestyle.deal_breaker_features.map((k, i) => (
                    <span key={i} className="badge badge-danger" style={{ marginRight: '4px', marginBottom: '4px' }}>{k}</span>
                  ))
                  : '—'}
              </div>
            </div>
          </div>

          {persona.ai_recommended_angle && (
            <div className="persona-field" style={{ marginTop: '14px' }}>
              <div className="field-label">AI Sales Angle</div>
              <div className="gold-block">{persona.ai_recommended_angle}</div>
            </div>
          )}

          {persona.next_best_action && (
            <div className="persona-field" style={{ marginTop: '10px' }}>
              <div className="field-label">Next Best Action</div>
              <div className="field-value">{persona.next_best_action}</div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
