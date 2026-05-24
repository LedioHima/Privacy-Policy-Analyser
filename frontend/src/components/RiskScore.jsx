import { useEffect, useState } from 'react'

const LABEL_CONFIG = {
  'LOW RISK':      { color: '#10b981', bg: '#052e1c', ring: '#064e32' },
  'MODERATE RISK': { color: '#f59e0b', bg: '#2d1f04', ring: '#4d3408' },
  'HIGH RISK':     { color: '#f97316', bg: '#2d1604', ring: '#4d2a08' },
  'CRITICAL RISK': { color: '#ef4444', bg: '#2d0a0a', ring: '#4d1212' },
}

export default function RiskScore({ score, label }) {
  const [displayScore, setDisplayScore] = useState(0)
  const config = LABEL_CONFIG[label] || LABEL_CONFIG['HIGH RISK']

  // Animate counter from 0 to score
  useEffect(() => {
    let start = 0
    const step = Math.ceil(score / 40)
    const timer = setInterval(() => {
      start = Math.min(start + step, score)
      setDisplayScore(start)
      if (start >= score) clearInterval(timer)
    }, 30)
    return () => clearInterval(timer)
  }, [score])

  // SVG ring params
  const radius = 70
  const circ   = 2 * Math.PI * radius
  const dash   = (score / 100) * circ

  return (
    <div className="flex flex-col items-center gap-4 fade-up">
      {/* Circular ring */}
      <div className="relative flex items-center justify-center" style={{ width: 180, height: 180 }}>
        {/* Glow ring */}
        <div className="absolute inset-0 rounded-full"
             style={{
               background: `radial-gradient(circle, ${config.ring}88 0%, transparent 70%)`,
               animation: 'pulse-ring 2s ease-in-out infinite',
             }} />

        <svg width="180" height="180" style={{ transform: 'rotate(-90deg)' }}>
          {/* Track */}
          <circle cx="90" cy="90" r={radius}
            fill="none" stroke="var(--bg3)" strokeWidth="10" />
          {/* Progress */}
          <circle cx="90" cy="90" r={radius}
            fill="none"
            stroke={config.color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circ}`}
            style={{ transition: 'stroke-dasharray 1s ease', filter: `drop-shadow(0 0 8px ${config.color})` }}
          />
        </svg>

        {/* Score number */}
        <div className="absolute flex flex-col items-center">
          <span className="text-5xl font-bold" style={{
            color: config.color,
            fontFamily: 'Space Mono, monospace',
            textShadow: `0 0 20px ${config.color}66`,
            animation: 'countUp 0.5s ease',
          }}>
            {displayScore}
          </span>
          <span className="text-xs" style={{ color: 'var(--text-dim)' }}>/ 100</span>
        </div>
      </div>

      {/* Label badge */}
      <div className="px-5 py-2 rounded-full text-sm font-semibold tracking-wider"
           style={{
             background: config.bg,
             color:      config.color,
             border:     `1px solid ${config.color}44`,
             fontFamily: 'Space Mono, monospace',
           }}>
        {label}
      </div>
    </div>
  )
}
