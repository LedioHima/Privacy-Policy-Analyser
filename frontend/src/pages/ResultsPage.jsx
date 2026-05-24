import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import RiskScore     from '../components/RiskScore'
import CategoryCard  from '../components/CategoryCard'
import GdprChecklist from '../components/GdprChecklist'

export default function ResultsPage() {
  const navigate = useNavigate()
  const [result, setResult] = useState(null)

  useEffect(() => {
    const stored = sessionStorage.getItem('result')
    if (!stored) { navigate('/'); return }
    setResult(JSON.parse(stored))
  }, [])

  if (!result) return null

  const categories = Object.keys(result.category_counts)

  return (
    <main className="max-w-4xl mx-auto px-4 py-10">

      {/* Back button */}
      <button onClick={() => navigate('/')}
        className="mb-8 flex items-center gap-2 text-sm transition-colors duration-200"
        style={{ color: 'var(--text-dim)', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
        ← Analyze another policy
      </button>

      {/* Header */}
      <div className="mb-8 fade-up">
        <p className="text-xs mb-2" style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>
          ANALYSIS RESULTS
        </p>
        <h1 className="text-2xl font-bold mb-1 break-all" style={{ color: 'var(--text)' }}>
          {result.url}
        </h1>
        <p className="text-sm" style={{ color: 'var(--text-dim)' }}>
          Analyzed {result.analyzed_at} · {result.total_sentences.toLocaleString()} sentences · {result.total_findings} risky clauses found
          {result.cached && <span className="ml-2 px-2 py-0.5 rounded text-xs"
            style={{ background: 'var(--bg3)', color: 'var(--accent)', border: '1px solid var(--border)' }}>cached</span>}
        </p>
      </div>

      {/* Top row — score + stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

        {/* Score */}
        <div className="md:col-span-1 rounded-2xl p-6 flex flex-col items-center justify-center fade-up"
             style={{ background: 'var(--bg2)', border: '1px solid var(--border)' }}>
          <RiskScore score={result.risk_score} label={result.risk_label} />
        </div>

        {/* Stats grid */}
        <div className="md:col-span-2 grid grid-cols-2 gap-4 fade-up-delay">
          {[
            { label: 'Total Sentences',   value: result.total_sentences.toLocaleString(), icon: '📄' },
            { label: 'Risky Clauses',     value: result.total_findings,                   icon: '⚠️' },
            { label: 'HIGH Severity',     value: result.findings.filter(f=>f.severity==='HIGH').length,   icon: '🔴' },
            { label: 'MEDIUM Severity',   value: result.findings.filter(f=>f.severity==='MEDIUM').length, icon: '🟡' },
          ].map(({ label, value, icon }) => (
            <div key={label} className="rounded-xl p-5"
                 style={{ background: 'var(--bg2)', border: '1px solid var(--border)' }}>
              <div className="text-2xl mb-2">{icon}</div>
              <div className="text-3xl font-bold mb-1"
                   style={{ color: 'var(--text)', fontFamily: 'Space Mono, monospace' }}>
                {value}
              </div>
              <div className="text-xs" style={{ color: 'var(--text-dim)' }}>{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Category breakdown */}
      <section className="mb-8 fade-up">
        <h2 className="text-sm font-semibold mb-4"
            style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>
          RISK BREAKDOWN BY CATEGORY
          <span className="ml-2 font-normal">(click to expand findings)</span>
        </h2>
        <div className="flex flex-col gap-3">
          {categories.map(cat => (
            <CategoryCard
              key={cat}
              category={cat}
              counts={result.category_counts[cat]}
              findings={result.findings}
            />
          ))}
        </div>
      </section>

      {/* GDPR Checklist */}
      <section className="fade-up">
        <h2 className="text-sm font-semibold mb-4"
            style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>
          GDPR COMPLIANCE CHECK
        </h2>
        <GdprChecklist findings={result.findings} />
      </section>
    </main>
  )
}
