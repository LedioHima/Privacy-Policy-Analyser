const CHECKS = [
  {
    label:    'Right to Erasure (Art. 17)',
    desc:     'Users can request their data be permanently deleted.',
    category: 'No Right to Deletion',
  },
  {
    label:    'No Data Selling (Art. 6)',
    desc:     'Personal data is not sold or shared with third parties for profit.',
    category: 'Data Selling & Third-Party Sharing',
  },
  {
    label:    'Data Minimization (Art. 5)',
    desc:     'Only necessary location data is collected with clear purpose.',
    category: 'Location Tracking',
  },
  {
    label:    'Storage Limitation (Art. 5)',
    desc:     'Data is deleted after a defined and reasonable retention period.',
    category: 'Indefinite Data Retention',
  },
  {
    label:    'Child Protection (Art. 8)',
    desc:     "Children's data is collected only with verifiable parental consent.",
    category: "Children's Data Collection",
  },
  {
    label:    'Transparency on Profiling (Art. 22)',
    desc:     'Users are clearly informed of automated profiling practices.',
    category: 'Behavioral Profiling',
  },
  {
    label:    'Law Enforcement Disclosure (Art. 23)',
    desc:     'Data shared with authorities only under strict legal obligation.',
    category: 'Law Enforcement & Government Sharing',
  },
]

export default function GdprChecklist({ findings }) {
  const flaggedCategories = new Set(findings.map(f => f.category))

  const pass = CHECKS.filter(c => !flaggedCategories.has(c.category))
  const fail = CHECKS.filter(c =>  flaggedCategories.has(c.category))

  return (
    <div className="rounded-xl overflow-hidden"
         style={{ background: 'var(--bg2)', border: '1px solid var(--border)' }}>

      <div className="px-5 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
        <h3 className="text-sm font-semibold" style={{ color: 'var(--text)', margin: 0, fontFamily: 'Space Mono, monospace' }}>
          GDPR Compliance Checklist
        </h3>
        <p className="text-xs mt-1" style={{ color: 'var(--text-dim)', margin: '4px 0 0' }}>
          {pass.length}/{CHECKS.length} requirements satisfied
        </p>
      </div>

      {/* Progress bar */}
      <div className="h-1.5" style={{ background: 'var(--bg3)' }}>
        <div className="h-full transition-all duration-700"
             style={{
               width: `${(pass.length / CHECKS.length) * 100}%`,
               background: pass.length === CHECKS.length
                 ? 'var(--green)'
                 : pass.length > CHECKS.length / 2
                   ? 'var(--yellow)'
                   : 'var(--red)',
             }} />
      </div>

      {/* Items */}
      <div className="divide-y" style={{ borderColor: 'var(--border)' }}>
        {CHECKS.map((check, i) => {
          const passed = !flaggedCategories.has(check.category)
          return (
            <div key={i} className="flex items-start gap-4 px-5 py-3.5">
              <div className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs mt-0.5"
                   style={{
                     background: passed ? '#052e1c' : '#2d0a0a',
                     color:      passed ? 'var(--green)' : 'var(--red)',
                     border:     `1px solid ${passed ? '#064e32' : '#4d1212'}`,
                   }}>
                {passed ? '✓' : '✗'}
              </div>
              <div>
                <p className="text-sm font-medium" style={{ color: passed ? 'var(--text)' : 'var(--text-dim)', margin: 0 }}>
                  {check.label}
                </p>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-dim)', margin: '2px 0 0' }}>
                  {check.desc}
                </p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
