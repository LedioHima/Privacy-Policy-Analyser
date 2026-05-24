import { useState } from 'react'

const CATEGORIES = [
  'Data Selling & Third-Party Sharing',
  'Location Tracking',
  'Indefinite Data Retention',
  'No Right to Deletion',
  'Behavioral Profiling',
  "Children's Data Collection",
  'Law Enforcement & Government Sharing',
]

const LABEL_COLOR = {
  'LOW RISK':      { color: 'var(--green)',  bg: '#052e1c' },
  'MODERATE RISK': { color: 'var(--yellow)', bg: '#2d1f04' },
  'HIGH RISK':     { color: 'var(--orange)', bg: '#2d1604' },
  'CRITICAL RISK': { color: 'var(--red)',    bg: '#2d0a0a' },
}

function ScoreBlock({ result }) {
  if (!result) return null
  const cfg = LABEL_COLOR[result.risk_label] || LABEL_COLOR['HIGH RISK']
  return (
    <div className="flex flex-col items-center gap-2 py-4">
      <div className="text-5xl font-bold" style={{ color: cfg.color, fontFamily: 'Space Mono, monospace' }}>
        {result.risk_score}
      </div>
      <div className="text-xs px-3 py-1 rounded-full" style={{ background: cfg.bg, color: cfg.color }}>
        {result.risk_label}
      </div>
    </div>
  )
}

export default function ComparePage() {
  const [urlA, setUrlA] = useState('')
  const [urlB, setUrlB] = useState('')
  const [resA, setResA] = useState(null)
  const [resB, setResB] = useState(null)
  const [loadingA, setLoadingA] = useState(false)
  const [loadingB, setLoadingB] = useState(false)
  const [errorA, setErrorA] = useState('')
  const [errorB, setErrorB] = useState('')

  async function analyze(url, setRes, setLoading, setError) {
    if (!url.trim()) return
    setLoading(true)
    setError('')
    try {
      const res  = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      })
      const data = await res.json()
      if (!res.ok) { setError(data.error || 'Failed'); return }
      setRes(data)
    } catch {
      setError('Server unreachable')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-10">
      <div className="mb-8 fade-up">
        <p className="text-xs mb-2" style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>
          SIDE-BY-SIDE COMPARISON
        </p>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text)' }}>
          Compare Two Privacy Policies
        </h1>
      </div>

      {/* URL inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 fade-up">
        {[
          { label: 'Policy A', url: urlA, setUrl: setUrlA, res: resA, loading: loadingA, error: errorA,
            onAnalyze: () => analyze(urlA, setResA, setLoadingA, setErrorA) },
          { label: 'Policy B', url: urlB, setUrl: setUrlB, res: resB, loading: loadingB, error: errorB,
            onAnalyze: () => analyze(urlB, setResB, setLoadingB, setErrorB) },
        ].map(({ label, url, setUrl, res, loading, error, onAnalyze }) => (
          <div key={label} className="rounded-xl p-5"
               style={{ background: 'var(--bg2)', border: '1px solid var(--border)' }}>
            <p className="text-xs mb-3 font-semibold" style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>
              {label}
            </p>
            <div className="flex gap-2 mb-2">
              <input
                type="url"
                placeholder="https://company.com/privacy"
                value={url}
                onChange={e => setUrl(e.target.value)}
                className="flex-1 px-3 py-2.5 rounded-lg text-sm outline-none"
                style={{ background: 'var(--bg3)', border: '1px solid var(--border)', color: 'var(--text)', fontFamily: 'Space Mono, monospace' }}
              />
              <button onClick={onAnalyze} disabled={!url.trim() || loading}
                className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                style={{ background: url.trim() ? 'var(--accent)' : 'var(--bg3)', color: 'white', cursor: url.trim() ? 'pointer' : 'not-allowed' }}>
                {loading ? '...' : 'Go'}
              </button>
            </div>
            {error && <p className="text-xs mt-1" style={{ color: 'var(--red)' }}>{error}</p>}
            {res && <ScoreBlock result={res} />}
          </div>
        ))}
      </div>

      {/* Category comparison table */}
      {resA && resB && (
        <div className="rounded-xl overflow-hidden fade-up"
             style={{ background: 'var(--bg2)', border: '1px solid var(--border)' }}>
          {/* Header */}
          <div className="grid grid-cols-3 px-5 py-3"
               style={{ background: 'var(--bg3)', borderBottom: '1px solid var(--border)' }}>
            <div className="text-xs font-semibold" style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>CATEGORY</div>
            <div className="text-xs font-semibold text-center" style={{ color: 'var(--accent)', fontFamily: 'Space Mono, monospace' }}>POLICY A</div>
            <div className="text-xs font-semibold text-center" style={{ color: 'var(--accent2)', fontFamily: 'Space Mono, monospace' }}>POLICY B</div>
          </div>

          {CATEGORIES.map((cat, i) => {
            const a = resA.category_counts[cat] || { total: 0, high: 0, medium: 0 }
            const b = resB.category_counts[cat] || { total: 0, high: 0, medium: 0 }

            function badge(counts) {
              if (counts.total === 0) return <span className="text-xs px-2 py-0.5 rounded font-mono" style={{ background: '#052e1c', color: 'var(--green)' }}>CLEAN</span>
              if (counts.high > 0)   return <span className="text-xs px-2 py-0.5 rounded font-mono" style={{ background: '#2d0a0a', color: 'var(--red)' }}>{counts.high}H {counts.medium}M</span>
              return <span className="text-xs px-2 py-0.5 rounded font-mono" style={{ background: '#2d1f04', color: 'var(--yellow)' }}>{counts.medium} MED</span>
            }

            return (
              <div key={cat} className="grid grid-cols-3 px-5 py-3.5 items-center"
                   style={{ borderBottom: i < CATEGORIES.length - 1 ? '1px solid var(--border)' : 'none' }}>
                <div className="text-sm" style={{ color: 'var(--text)' }}>{cat}</div>
                <div className="flex justify-center">{badge(a)}</div>
                <div className="flex justify-center">{badge(b)}</div>
              </div>
            )
          })}

          {/* Score comparison bar */}
          <div className="px-5 py-5" style={{ borderTop: '1px solid var(--border)', background: 'var(--bg3)' }}>
            <p className="text-xs mb-4" style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>RISK SCORE COMPARISON</p>
            {[{ label: 'Policy A', score: resA.risk_score, color: 'var(--accent)' },
              { label: 'Policy B', score: resB.risk_score, color: 'var(--accent2)' }
            ].map(({ label, score, color }) => (
              <div key={label} className="mb-3">
                <div className="flex justify-between text-xs mb-1" style={{ color: 'var(--text-dim)' }}>
                  <span>{label}</span><span style={{ color, fontFamily: 'Space Mono' }}>{score}/100</span>
                </div>
                <div className="h-2 rounded-full" style={{ background: 'var(--bg2)' }}>
                  <div className="h-full rounded-full transition-all duration-700"
                       style={{ width: `${score}%`, background: color }} />
                </div>
              </div>
            ))}
            <p className="text-sm mt-4 font-medium" style={{ color: 'var(--text)' }}>
              {resA.risk_score < resB.risk_score
                ? `✓ Policy A is ${resB.risk_score - resA.risk_score} points safer than Policy B`
                : resB.risk_score < resA.risk_score
                  ? `✓ Policy B is ${resA.risk_score - resB.risk_score} points safer than Policy A`
                  : '= Both policies have the same risk score'}
            </p>
          </div>
        </div>
      )}
    </main>
  )
}
