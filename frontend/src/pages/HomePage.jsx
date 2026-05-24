import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import LoadingScanner from '../components/LoadingScanner'

const QUICK_LINKS = [
  { label: 'Google',     url: 'https://policies.google.com/privacy' },
  { label: 'Apple',      url: 'https://www.apple.com/legal/privacy/en-ww/' },
  { label: 'Microsoft',  url: 'https://privacy.microsoft.com/en-us/privacystatement' },
  { label: 'TikTok',     url: 'https://www.tiktok.com/legal/page/us/privacy-policy/en' },
  { label: 'Twitter/X',  url: 'https://twitter.com/en/privacy' },
  { label: 'LinkedIn',   url: 'https://www.linkedin.com/legal/privacy-policy' },
  { label: 'Spotify',    url: 'https://www.spotify.com/us/legal/privacy-policy/' },
  { label: 'Airbnb',     url: 'https://www.airbnb.com/help/article/2855' },
  { label: 'Zoom',       url: 'https://explore.zoom.us/en/privacy/' },
  { label: 'DuckDuckGo', url: 'https://duckduckgo.com/privacy' },
]

export default function HomePage() {
  const navigate  = useNavigate()
  const [url,     setUrl]     = useState('')
  const [text,    setText]    = useState('')
  const [mode,    setMode]    = useState('url')   // 'url' | 'text'
  const [loading, setLoading] = useState(false)
  const [step,    setStep]    = useState(0)
  const [error,   setError]   = useState('')

  async function handleAnalyze() {
    setError('')
    setLoading(true)
    setStep(0)

    // Simulate step progression while waiting
    const stepTimer = setInterval(() => setStep(s => Math.min(s + 1, 4)), 2500)

    try {
      const endpoint = mode === 'url' ? '/api/analyze' : '/api/analyze/text'
      const body     = mode === 'url'
        ? { url: url.trim() }
        : { text: text.trim(), label: 'Pasted Policy' }

      const res  = await fetch(endpoint, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(body),
      })
      const data = await res.json()

      if (!res.ok) {
        setError(data.error || 'Analysis failed. Please try again.')
        return
      }

      // Store result in sessionStorage and navigate to results page
      sessionStorage.setItem('result', JSON.stringify(data))
      navigate('/results')

    } catch (e) {
      setError('Could not reach the server. Is Flask running on port 5000?')
    } finally {
      clearInterval(stepTimer)
      setLoading(false)
      setStep(0)
    }
  }

  if (loading) {
    return (
      <main className="flex flex-col items-center justify-center min-h-[80vh] px-4">
        <LoadingScanner step={step} />
      </main>
    )
  }

  return (
    <main className="max-w-3xl mx-auto px-4 py-16">

      {/* Hero */}
      <div className="text-center mb-12 fade-up">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs mb-6"
             style={{ background: 'var(--bg3)', color: 'var(--accent)', border: '1px solid var(--border)', fontFamily: 'Space Mono, monospace' }}>
          🔒 NLP-Powered Privacy Analysis
        </div>
        <h1 className="text-5xl font-bold mb-4 leading-tight tracking-tight"
            style={{ color: 'var(--text)', fontFamily: 'Space Mono, monospace' }}>
          Privacy<br/>
          <span style={{ color: 'var(--accent)' }}>Policy</span> Scanner
        </h1>
        <p className="text-lg" style={{ color: 'var(--text-dim)', maxWidth: 480, margin: '0 auto' }}>
          Paste a URL. Get a risk score in seconds. Know exactly what you're agreeing to.
        </p>
      </div>

      {/* Input card */}
      <div className="rounded-2xl p-6 mb-6 fade-up-delay"
           style={{ background: 'var(--bg2)', border: '1px solid var(--border)' }}>

        {/* Mode toggle */}
        <div className="flex gap-1 p-1 rounded-lg mb-5 w-fit"
             style={{ background: 'var(--bg3)' }}>
          {[['url', '🔗 URL'], ['text', '📋 Paste Text']].map(([m, label]) => (
            <button key={m} onClick={() => setMode(m)}
              className="px-4 py-2 rounded-md text-sm font-medium transition-all duration-200"
              style={{
                background: mode === m ? 'var(--bg2)' : 'transparent',
                color:      mode === m ? 'var(--text)' : 'var(--text-dim)',
                border:     mode === m ? '1px solid var(--border)' : '1px solid transparent',
              }}>
              {label}
            </button>
          ))}
        </div>

        {mode === 'url' ? (
          <div className="flex gap-3">
            <input
              type="url"
              placeholder="https://company.com/privacy"
              value={url}
              onChange={e => setUrl(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleAnalyze()}
              className="flex-1 px-4 py-3 rounded-xl text-sm outline-none transition-all duration-200"
              style={{
                background:  'var(--bg3)',
                border:      '1px solid var(--border)',
                color:       'var(--text)',
                fontFamily:  'Space Mono, monospace',
              }}
            />
            <button onClick={handleAnalyze} disabled={!url.trim()}
              className="px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-200"
              style={{
                background: url.trim() ? 'var(--accent)' : 'var(--bg3)',
                color:      url.trim() ? 'white' : 'var(--text-dim)',
                cursor:     url.trim() ? 'pointer' : 'not-allowed',
              }}>
              Analyze →
            </button>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            <textarea
              rows={8}
              placeholder="Paste the full privacy policy text here..."
              value={text}
              onChange={e => setText(e.target.value)}
              className="w-full px-4 py-3 rounded-xl text-sm outline-none resize-none"
              style={{
                background: 'var(--bg3)',
                border:     '1px solid var(--border)',
                color:      'var(--text)',
              }}
            />
            <button onClick={handleAnalyze} disabled={text.trim().length < 100}
              className="px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-200 self-end"
              style={{
                background: text.trim().length >= 100 ? 'var(--accent)' : 'var(--bg3)',
                color:      text.trim().length >= 100 ? 'white' : 'var(--text-dim)',
                cursor:     text.trim().length >= 100 ? 'pointer' : 'not-allowed',
              }}>
              Analyze →
            </button>
          </div>
        )}

        {error && (
          <p className="mt-3 text-sm px-3 py-2 rounded-lg"
             style={{ color: 'var(--red)', background: '#2d0a0a', border: '1px solid #4d1212' }}>
            {error}
          </p>
        )}
      </div>

      {/* Quick links */}
      <div className="fade-up-delay">
        <p className="text-xs mb-3 text-center" style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>
          QUICK ANALYZE
        </p>
        <div className="flex gap-2 flex-wrap justify-center">
          {QUICK_LINKS.map(({ label, url: u }) => (
            <button key={label} onClick={() => { setUrl(u); setMode('url') }}
              className="px-4 py-2 rounded-lg text-sm transition-all duration-200"
              style={{
                background: 'var(--bg2)',
                color:      'var(--text-dim)',
                border:     '1px solid var(--border)',
              }}>
              {label}
            </button>
          ))}
        </div>
      </div>
    </main>
  )
}
