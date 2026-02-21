import { useState, useEffect, useRef } from 'react'
import './VoiceInterface.css'

export default function VoiceInterface({ apiBase, onNavigate }) {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [status, setStatus] = useState('idle')
  const [personaId, setPersonaId] = useState(null)
  const [persona, setPersona] = useState(null)
  const [propertyId, setPropertyId] = useState('')
  const [brokerId, setBrokerId] = useState('')
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [speechSupported, setSpeechSupported] = useState(true)

  const recognitionRef = useRef(null)
  const audioPlayerRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Initialize Web Speech API
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      setSpeechSupported(false)
      console.error('Web Speech API not supported in this browser')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsListening(true)
      setTranscript('')
      setInterimTranscript('')
    }

    recognition.onresult = (event) => {
      let interim = ''
      let final = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          final += transcript + ' '
        } else {
          interim += transcript
        }
      }

      if (final) {
        setTranscript(prev => (prev + final).trim())
      }
      setInterimTranscript(interim)
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      if (event.error === 'no-speech') {
        // User didn't speak, just restart
        return
      }
      setIsListening(false)
      if (event.error !== 'aborted') {
        alert(`Speech recognition error: ${event.error}`)
      }
    }

    recognition.onend = () => {
      if (isListening && !isProcessing) {
        // Auto-restart if still supposed to be listening
        try {
          recognition.start()
        } catch (e) {
          // Already started, ignore
        }
      }
    }

    recognitionRef.current = recognition

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
      }
    }
  }, [])

  const startListening = () => {
    if (!speechSupported) {
      alert('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.')
      return
    }

    if (recognitionRef.current) {
      setTranscript('')
      setInterimTranscript('')
      try {
        recognitionRef.current.start()
      } catch (error) {
        console.error('Error starting speech recognition:', error)
        alert('Failed to start speech recognition. Please try again.')
      }
    }
  }

  const stopListening = async () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      setIsListening(false)

      // Wait a bit for final results to come through
      await new Promise(resolve => setTimeout(resolve, 500))

      // Send the transcript if we have one
      if (transcript.trim()) {
        await sendTextMessage(transcript.trim())
      }
    }
  }

  const sendTextMessage = async (text) => {
    setIsProcessing(true)

    try {
      const res = await fetch(`${apiBase}/api/v1/persona/text-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          broker_id: brokerId || null,
          property_id: propertyId || null,
          message: text,
        }),
      })

      const data = await res.json()

      setSessionId(data.session_id)
      setStatus(data.session_status)

      // Add messages to chat history
      setMessages(prev => [
        ...prev,
        { role: 'user', content: text },
        { role: 'assistant', content: data.reply }
      ])

      // Convert reply to speech and play
      await playTextAsAudio(data.reply)

      // Check if persona is complete
      if (data.session_status === 'complete' && data.persona_id) {
        setPersonaId(data.persona_id)
        const personaRes = await fetch(`${apiBase}/api/v1/persona/${data.persona_id}`)
        if (personaRes.ok) {
          setPersona(await personaRes.json())
        }
      }
    } catch (error) {
      console.error('Error processing message:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠️ Failed to connect. Make sure the API server is running.',
      }])
    } finally {
      setIsProcessing(false)
      setTranscript('')
      setInterimTranscript('')
    }
  }

  const playTextAsAudio = async (text) => {
    try {
      setIsSpeaking(true)

      const formData = new FormData()
      formData.append('text', text)

      const response = await fetch(`${apiBase}/api/v1/persona/tts`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) throw new Error('TTS failed')

      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)

      if (audioPlayerRef.current) {
        audioPlayerRef.current.src = audioUrl
        audioPlayerRef.current.onended = () => {
          setIsSpeaking(false)
          URL.revokeObjectURL(audioUrl)
        }
        await audioPlayerRef.current.play()
      }
    } catch (error) {
      console.error('Error playing audio:', error)
      setIsSpeaking(false)
    }
  }

  const startNew = () => {
    setSessionId(null)
    setMessages([])
    setStatus('idle')
    setPersonaId(null)
    setPersona(null)
    setTranscript('')
    setInterimTranscript('')
    if (isListening && recognitionRef.current) {
      recognitionRef.current.abort()
      setIsListening(false)
    }
  }

  const handleToggleVoice = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  // Display current transcript (final + interim)
  const displayTranscript = transcript + (interimTranscript ? ' ' + interimTranscript : '')

  return (
    <div className="voice-container">
      <div className="page-header">
        <h1>🎙️ Voice Persona Builder</h1>
        <p>AI-powered voice conversation to build buyer personas</p>
      </div>

      {/* Config Row */}
      <div className="config-row">
        <div className="form-group">
          <label>Property ID (optional)</label>
          <input
            className="input"
            placeholder="e.g. prop_dubai_creek"
            value={propertyId}
            onChange={e => setPropertyId(e.target.value)}
            disabled={status !== 'idle'}
          />
        </div>
        <div className="form-group">
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
      <div className="status-row">
        <span className={`badge ${
          status === 'complete' ? 'badge-success' :
          status === 'collecting' ? 'badge-warning' : 'badge-info'
        }`}>
          {status === 'complete' ? '✅ Persona Complete' :
           status === 'collecting' ? '🔄 Collecting Information' : '🎤 Ready to Start'}
        </span>
        {sessionId && (
          <span className="session-id">Session: {sessionId}</span>
        )}
      </div>

      {/* Voice Interface */}
      <div className="voice-interface">
        {/* Voice Visualizer */}
        <div className="voice-visualizer">
          <div className={`voice-orb ${isListening ? 'listening' : ''} ${isSpeaking ? 'speaking' : ''} ${isProcessing ? 'processing' : ''}`}>
            <div className="orb-inner">
              {isListening && <span className="status-icon">🎤</span>}
              {isSpeaking && <span className="status-icon">🔊</span>}
              {isProcessing && <span className="status-icon">⚙️</span>}
              {!isListening && !isSpeaking && !isProcessing && <span className="status-icon">💬</span>}
            </div>
            {isListening && (
              <div className="pulse-rings">
                <div className="pulse-ring pulse-ring-1"></div>
                <div className="pulse-ring pulse-ring-2"></div>
                <div className="pulse-ring pulse-ring-3"></div>
              </div>
            )}
          </div>

          <div className="voice-status">
            {isListening && <p>Listening... Speak now</p>}
            {isProcessing && <p>Processing your message...</p>}
            {isSpeaking && <p>AI is speaking...</p>}
            {!isListening && !isProcessing && !isSpeaking && (
              <p>Tap the microphone to start</p>
            )}
          </div>

          {displayTranscript && (
            <div className="transcript-preview">
              <span className="transcript-label">{isListening ? 'Listening:' : 'You said:'}</span>
              <span className="transcript-text">
                {transcript}
                {interimTranscript && (
                  <span style={{ opacity: 0.6, fontStyle: 'italic' }}> {interimTranscript}</span>
                )}
              </span>
            </div>
          )}

          {!speechSupported && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              background: 'rgba(239, 68, 68, 0.1)',
              borderRadius: '8px',
              color: 'var(--danger)'
            }}>
              ⚠️ Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.
            </div>
          )}
        </div>

        {/* Voice Controls */}
        <div className="voice-controls">
          <button
            className={`voice-btn ${isListening ? 'active' : ''}`}
            onClick={handleToggleVoice}
            disabled={isProcessing || isSpeaking || status === 'complete'}
          >
            {isListening ? (
              <>
                <span className="btn-icon">⏹️</span>
                <span>Stop Recording</span>
              </>
            ) : (
              <>
                <span className="btn-icon">🎤</span>
                <span>Start Speaking</span>
              </>
            )}
          </button>
        </div>

        {/* Chat History */}
        {messages.length > 0 && (
          <div className="chat-history">
            <h3>Conversation History</h3>
            <div className="chat-messages-compact">
              {messages.map((msg, i) => (
                <div key={i} className={`message-compact ${msg.role}`}>
                  <div className="message-sender">
                    {msg.role === 'user' ? '👤 You' : '🤖 AI'}
                  </div>
                  <div className="message-content">{msg.content}</div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}
      </div>

      {/* Persona Preview */}
      {persona && (
        <div className="persona-preview">
          <div className="persona-header">
            <div className="persona-avatar">👤</div>
            <div>
              <h2>{persona.persona_type || 'Buyer'} Persona</h2>
              <span className="persona-id">{persona.persona_id}</span>
            </div>
            <div className="trust-score">
              <div className="score-value">{persona.trust_level_score}</div>
              <div className="score-label">Trust Score</div>
            </div>
          </div>

          <div className="persona-grid">
            <div className="persona-field">
              <div className="field-label">Primary Motivation</div>
              <div className="field-value">{persona.primary_motivation || '—'}</div>
            </div>
            <div className="persona-field">
              <div className="field-label">Nationality</div>
              <div className="field-value">{persona.demographic_context?.nationality || '—'}</div>
            </div>
            <div className="persona-field">
              <div className="field-label">Key Interests</div>
              <div className="field-value">
                {(persona.key_interests || []).map((k, i) => (
                  <span key={i} className="badge badge-primary">
                    {k}
                  </span>
                ))}
              </div>
            </div>
            <div className="persona-field">
              <div className="field-label">Ignored Features</div>
              <div className="field-value">
                {(persona.ignored_features || []).map((k, i) => (
                  <span key={i} className="badge badge-danger">
                    {k}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {persona.ai_recommended_angle && (
            <div className="persona-field recommended-angle">
              <div className="field-label">AI Recommended Sales Angle</div>
              <div className="field-value">
                💡 {persona.ai_recommended_angle}
              </div>
            </div>
          )}

          {persona.next_best_action && (
            <div className="persona-field">
              <div className="field-label">Next Best Action</div>
              <div className="field-value">{persona.next_best_action}</div>
            </div>
          )}
        </div>
      )}

      {/* Hidden audio player */}
      <audio ref={audioPlayerRef} style={{ display: 'none' }} />
    </div>
  )
}
