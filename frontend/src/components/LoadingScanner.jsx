const STEPS = [
  { icon: '🌐', label: 'Fetching privacy policy...' },
  { icon: '🧹', label: 'Cleaning HTML content...' },
  { icon: '✂️',  label: 'Splitting into sentences...' },
  { icon: '🔍', label: 'Scanning for risky clauses...' },
  { icon: '⚖️',  label: 'Calculating risk score...' },
]

export default function LoadingScanner({ step = 0 }) {
  return (
    <div className="flex flex-col items-center gap-8 py-16 fade-up">

      {/* Scanning animation */}
      <div className="relative w-48 h-48">
        {/* Outer ring */}
        <div className="absolute inset-0 rounded-full"
             style={{ border: '1px solid var(--border)' }} />
        {/* Spinning ring */}
        <div className="absolute inset-2 rounded-full"
             style={{
               border: '2px solid transparent',
               borderTopColor: 'var(--accent)',
               animation: 'spin 1s linear infinite',
             }} />
        {/* Inner ring */}
        <div className="absolute inset-6 rounded-full"
             style={{
               border: '1px solid var(--border)',
               animation: 'spin 2s linear infinite reverse',
               borderTopColor: 'var(--accent2)',
             }} />
        {/* Center icon */}
        <div className="absolute inset-0 flex items-center justify-center text-4xl">
          {STEPS[Math.min(step, STEPS.length - 1)].icon}
        </div>

        {/* Scan line */}
        <div className="absolute left-0 right-0"
             style={{
               top: '50%',
               height: '1px',
               background: `linear-gradient(90deg, transparent, var(--accent), transparent)`,
               animation: 'scan 1.5s ease-in-out infinite',
               opacity: 0.6,
             }} />
      </div>

      {/* Steps */}
      <div className="flex flex-col gap-2 w-full max-w-xs">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-300"
               style={{
                 background: i === step ? 'var(--bg3)' : 'transparent',
                 border:     i === step ? '1px solid var(--border)' : '1px solid transparent',
                 opacity:    i > step ? 0.3 : 1,
               }}>
            <span className="text-base">{s.icon}</span>
            <span className="text-sm" style={{
              color:      i === step ? 'var(--accent)' : i < step ? 'var(--green)' : 'var(--text-dim)',
              fontFamily: i === step ? 'Space Mono, monospace' : 'inherit',
            }}>
              {i < step && '✓ '}{s.label}
            </span>
            {i === step && (
              <span className="ml-auto text-xs" style={{ color: 'var(--accent)', animation: 'pulse 1s infinite' }}>
                ●
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
