// Chat page (UI: AL, backend: JF). Streams /api/chat and shows which tools produced the answer.
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { chat } from './api'

const SUGGESTIONS = [
  'Will I lose power?',
  'How long could restoration take?',
  'What should I do to prepare?',
  'Do I qualify for outage alerts?',
]

export default function ChatPage({ storm, selected }) {
  const [messages, setMessages] = useState([]) // {role, content, trace?}
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  async function send(text) {
    const question = text.trim()
    if (!question || busy) return
    const history = [...messages, { role: 'user', content: question }]
    setMessages([...history, { role: 'assistant', content: '' }])
    setInput('')
    setBusy(true)
    const setLast = (patch) => setMessages((m) => [...m.slice(0, -1), { ...m.at(-1), ...patch }])
    try {
      const { text: reply, trace } = await chat(
        history.map(({ role, content }) => ({ role, content })),
        selected?.h3 ?? null,
        { storm },
        (partial) => setLast({ content: partial }),
      )
      setLast({ content: reply, trace })
    } catch {
      setLast({ content: "Sorry, I couldn't reach the assistant. If you're in danger or see a downed line, call 911." })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="chat">
      <div className="chat-context">
        {selected
          ? <>Asking about the area you selected: <strong>{selected.band} risk</strong>, about {selected.n_premises} homes. <Link to="/">Change</Link></>
          : <>No area selected. <Link to="/">Pick one on the map</Link> for answers about your location.</>}
      </div>

      <div className="chat-log" aria-live="polite">
        {messages.length === 0 && (
          <div className="suggestions">
            {SUGGESTIONS.map((s) => <button key={s} onClick={() => send(s)}>{s}</button>)}
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <p>{m.content || '…'}</p>
            {m.trace?.length > 0 && (
              <details>
                <summary>How I got this</summary>
                <ul>{m.trace.map((t, j) => <li key={j}><code>{t.tool}</code></li>)}</ul>
              </details>
            )}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      <form className="chat-input" onSubmit={(e) => { e.preventDefault(); send(input) }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about outages, restoration, or preparing…"
          aria-label="Message"
        />
        <button type="submit" disabled={busy || !input.trim()}>Send</button>
      </form>
    </div>
  )
}
