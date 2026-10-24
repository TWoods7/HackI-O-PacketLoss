// Thin client for docs/API_CONTRACT.md

const get = (path) => fetch(path).then((r) => r.json())
const post = (path, body) =>
  fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })

export const getHexes = (storm) => get(`/api/hexes?storm=${storm}`)
export const getLocation = (h3) => get(`/api/location?h3=${h3}`)
export const getRisk = (contextId, storm) => get(`/api/risk?context_id=${contextId}&storm=${storm}`)
export const getRestoration = (contextId, scenario) =>
  post('/api/restoration', { context_id: contextId, scenario }).then((r) => r.json())
export const getAlerts = (contextId, declaredNeeds, storm) =>
  post('/api/alerts', { context_id: contextId, declared_needs: declaredNeeds, storm }).then((r) => r.json())

// Streams the reply; calls onText(fullTextSoFar). Resolves to { text, trace }.
export async function chat(messages, contextId, scenario, onText) {
  const res = await post('/api/chat', { messages, context_id: contextId, scenario })
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let raw = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    raw += decoder.decode(value, { stream: true })
    onText(raw.split('\n[[TOOL_TRACE]]')[0])
  }
  const [text, trace] = raw.split('\n[[TOOL_TRACE]]')
  return { text, trace: trace ? JSON.parse(trace) : [] }
}
