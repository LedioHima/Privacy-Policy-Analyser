import { Link, useLocation } from 'react-router-dom'

const links = [
  { to: '/',        label: 'Analyze' },
  { to: '/history', label: 'History' },
  { to: '/compare', label: 'Compare' },
]

export default function Navbar() {
  const { pathname } = useLocation()

  return (
    <nav style={{ background: 'var(--bg2)', borderBottom: '1px solid var(--border)' }}
         className="sticky top-0 z-50 px-6 py-4 flex items-center justify-between">

      {/* Logo */}
      <Link to="/" className="flex items-center gap-3 no-underline">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
             style={{ background: 'var(--accent)', fontFamily: 'Space Mono, monospace' }}>
          PP
        </div>
        <span className="font-semibold text-base tracking-tight"
              style={{ color: 'var(--text)', fontFamily: 'Space Mono, monospace' }}>
          PrivacyScope
        </span>
      </Link>

      {/* Nav links */}
      <div className="flex items-center gap-1">
        {links.map(({ to, label }) => {
          const active = pathname === to
          return (
            <Link key={to} to={to}
              className="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 no-underline"
              style={{
                background: active ? 'var(--bg3)' : 'transparent',
                color:      active ? 'var(--accent)' : 'var(--text-dim)',
                border:     active ? '1px solid var(--border)' : '1px solid transparent',
              }}>
              {label}
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
