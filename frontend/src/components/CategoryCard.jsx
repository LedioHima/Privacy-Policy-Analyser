import { useState } from 'react'

const SEV_COLOR = {
  HIGH:   { text: '#ef4444', bg: '#2d0a0a', border: '#4d1212' },
  MEDIUM: { text: '#f59e0b', bg: '#2d1f04', border: '#4d3408' },
}

export default function CategoryCard({ category, counts, findings }) {
  const [open, setOpen] = useState(false)

  const catFindings = findings.filter(f => f.category === category)
  const isClean     = counts.total === 0

  return (
    <div className="rounded-xl overflow-hidden transition-all duration-200"
         style={{
           background: 'var(--bg2)',
           border: `1px solid ${isClean ? 'var(--border)' : counts.high > 0 ? '#4d121244' : '#4d340844'}`,
         }}>

      {/* Header row */}
      <button
        onClick={() => !isClean && setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 text-left transition-colors duration-200"
        style={{ cursor: isClean ? 'default' : 'pointer' }}
      >
        <div className="flex items-center gap-3">
          {/* Status dot */}
          <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{
            background: isClean
              ? 'var(--green)'
              : counts.high > 0 ? 'var(--red)' : 'var(--yellow)',
            boxShadow: isClean
              ? '0 0 6px var(--green)'
              : counts.high > 0 ? '0 0 6px var(--red)' : '0 0 6px var(--yellow)',
          }} />
          <span className="text-sm font-medium" style={{ color: 'var(--text)' }}>
            {category}
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Counts */}
          {counts.high > 0 && (
            <span className="text-xs px-2.5 py-1 rounded-full font-mono"
                  style={{ background: '#2d0a0a', color: 'var(--red)', border: '1px solid #4d1212' }}>
              {counts.high} HIGH
            </span>
          )}
          {counts.medium > 0 && (
            <span className="text-xs px-2.5 py-1 rounded-full font-mono"
                  style={{ background: '#2d1f04', color: 'var(--yellow)', border: '1px solid #4d3408' }}>
              {counts.medium} MED
            </span>
          )}
          {isClean && (
            <span className="text-xs px-2.5 py-1 rounded-full font-mono"
                  style={{ background: '#052e1c', color: 'var(--green)', border: '1px solid #064e32' }}>
              CLEAN
            </span>
          )}
          {/* Expand arrow */}
          {!isClean && (
            <span style={{ color: 'var(--text-dim)', transform: open ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }}>
              ▾
            </span>
          )}
        </div>
      </button>

      {/* Expanded findings */}
      {open && catFindings.length > 0 && (
        <div style={{ borderTop: '1px solid var(--border)' }}>
          {catFindings.map((f, i) => {
            const sev = SEV_COLOR[f.severity] || SEV_COLOR.HIGH
            return (
              <div key={i} className="px-5 py-4"
                   style={{ borderBottom: i < catFindings.length - 1 ? '1px solid var(--border)' : 'none' }}>

                {/* Severity + explanation */}
                <div className="flex items-start gap-3 mb-2">
                  <span className="text-xs px-2 py-0.5 rounded font-mono flex-shrink-0 mt-0.5"
                        style={{ background: sev.bg, color: sev.text, border: `1px solid ${sev.border}` }}>
                    {f.severity}
                  </span>
                  <p className="text-sm" style={{ color: 'var(--text)', margin: 0 }}>
                    {f.plain_english}
                  </p>
                </div>

                {/* Original clause */}
                <blockquote className="mt-2 pl-3 text-xs leading-relaxed"
                            style={{
                              borderLeft: `2px solid ${sev.text}44`,
                              color: 'var(--text-dim)',
                              fontStyle: 'italic',
                              margin: 0,
                            }}>
                  "{f.sentence.length > 250 ? f.sentence.slice(0, 250) + '…' : f.sentence}"
                </blockquote>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
