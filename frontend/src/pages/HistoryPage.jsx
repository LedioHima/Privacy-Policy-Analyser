import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const LABEL_COLOR = {
  'LOW RISK':      'var(--green)',
  'MODERATE RISK': 'var(--yellow)',
  'HIGH RISK':     'var(--red)',
  'CRITICAL RISK': 'var(--red)',
}

export default function HistoryPage() {
  const navigate = useNavigate()
  const [history, setHistory]     = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState('')
  const [selectedIds, setSelectedIds] = useState([])
  const [deleting, setDeleting]   = useState(false)

  const loadHistory = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const r = await fetch('/api/history')
      if (!r.ok) throw new Error('bad response')
      const data = await r.json()
      setHistory(data)
    } catch {
      setError('Could not load history. Is Flask running?')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  function toggleSelect(id) {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    )
  }

  function selectAll() {
    setSelectedIds(history.map(h => h.id))
  }

  function clearSelection() {
    setSelectedIds([])
  }

  async function loadResult(id) {
    const res  = await fetch(`/api/result/${id}`)
    const data = await res.json()
    sessionStorage.setItem('result', JSON.stringify(data))
    navigate('/results')
  }

  async function deleteOne(id, e) {
    e.stopPropagation()
    if (!window.confirm('Remove this analysis from history?')) return
    setDeleting(true)
    try {
      const res = await fetch(`/api/result/${id}`, { method: 'DELETE' })
      if (!res.ok) {
        setError('Could not delete. Try again.')
        return
      }
      setSelectedIds(prev => prev.filter(x => x !== id))
      await loadHistory()
    } catch {
      setError('Could not delete. Is Flask running?')
    } finally {
      setDeleting(false)
    }
  }

  async function deleteSelected() {
    if (selectedIds.length === 0) return
    if (!window.confirm(`Delete ${selectedIds.length} analysis result(s) from history?`)) return
    setDeleting(true)
    try {
      const res = await fetch('/api/history', {
        method:  'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ ids: selectedIds }),
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.error || 'Could not delete. Try again.')
        return
      }
      clearSelection()
      await loadHistory()
    } catch {
      setError('Could not delete. Is Flask running?')
    } finally {
      setDeleting(false)
    }
  }

  const allSelected = history.length > 0 && selectedIds.length === history.length
  const someSelected = selectedIds.length > 0

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">
      <div className="mb-8 fade-up">
        <p className="text-xs mb-2" style={{ color: 'var(--text-dim)', fontFamily: 'Space Mono, monospace' }}>
          ANALYSIS HISTORY
        </p>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text)' }}>
          Recently Analyzed Policies
        </h1>
      </div>

      {loading && <p style={{ color: 'var(--text-dim)' }}>Loading...</p>}
      {error   && <p style={{ color: 'var(--red)' }}>{error}</p>}

      {!loading && !error && history.length === 0 && (
        <div className="text-center py-16" style={{ color: 'var(--text-dim)' }}>
          <p className="text-4xl mb-4">🔍</p>
          <p>No policies analyzed yet.</p>
          <button onClick={() => navigate('/')} className="mt-4 underline"
                  style={{ color: 'var(--accent)', background: 'none', border: 'none', cursor: 'pointer' }}>
            Analyze your first policy →
          </button>
        </div>
      )}

      {!loading && !error && history.length > 0 && (
        <div className="mb-4 flex flex-wrap items-center gap-2 fade-up"
             style={{ fontFamily: 'Space Mono, monospace' }}>
          <span className="text-xs" style={{ color: 'var(--text-dim)' }}>Select</span>
          <button
            type="button"
            onClick={allSelected ? clearSelection : selectAll}
            className="px-3 py-1.5 rounded-lg text-xs transition-all duration-200"
            style={{
              background: 'var(--bg2)',
              color:      'var(--text-dim)',
              border:     '1px solid var(--border)',
              cursor:     'pointer',
            }}
          >
            {allSelected ? 'Deselect all' : 'Select all'}
          </button>
          <button
            type="button"
            onClick={deleteSelected}
            disabled={!someSelected || deleting}
            className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200"
            style={{
              background: someSelected && !deleting ? '#2d0a0a' : 'var(--bg3)',
              color:      someSelected && !deleting ? 'var(--red)' : 'var(--text-dim)',
              border:     '1px solid ' + (someSelected && !deleting ? '#4d1212' : 'var(--border)'),
              cursor:     someSelected && !deleting ? 'pointer' : 'not-allowed',
            }}
          >
            {deleting ? 'Removing…' : `Delete selected${someSelected ? ` (${selectedIds.length})` : ''}`}
          </button>
        </div>
      )}

      <div className="flex flex-col gap-3">
        {history.map(item => {
          const checked = selectedIds.includes(item.id)
          return (
            <div
              key={item.id}
              className="w-full rounded-xl p-1 flex items-stretch gap-1 transition-all duration-200 group"
              style={{ background: 'var(--bg2)', border: '1px solid var(--border)' }}
            >
              <label
                className="flex items-center pl-3 pr-1 cursor-pointer flex-shrink-0"
                onClick={e => e.stopPropagation()}
                style={{ userSelect: 'none' }}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleSelect(item.id)}
                  className="w-4 h-4 rounded cursor-pointer"
                  style={{ accentColor: 'var(--accent)' }}
                />
              </label>

              <button
                type="button"
                onClick={() => !deleting && loadResult(item.id)}
                disabled={deleting}
                className="flex-1 min-w-0 rounded-lg p-4 text-left transition-all duration-200"
                style={{ background: 'transparent', border: 'none', cursor: deleting ? 'wait' : 'pointer' }}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate mb-1" style={{ color: 'var(--text)' }}>
                      {item.url}
                    </p>
                    <p className="text-xs" style={{ color: 'var(--text-dim)' }}>
                      {item.analyzed_at} · {item.total_sentences?.toLocaleString()} sentences · {item.total_findings} findings
                    </p>
                  </div>
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className="text-right">
                      <div className="text-2xl font-bold" style={{
                        color: LABEL_COLOR[item.risk_label] || 'var(--red)',
                        fontFamily: 'Space Mono, monospace',
                      }}>
                        {item.risk_score}
                      </div>
                      <div className="text-xs" style={{ color: 'var(--text-dim)' }}>/100</div>
                    </div>
                    <span style={{ color: 'var(--text-dim)' }}>→</span>
                  </div>
                </div>
              </button>

              <div className="flex items-center pr-2 flex-shrink-0">
                <button
                  type="button"
                  onClick={e => deleteOne(item.id, e)}
                  disabled={deleting}
                  className="px-2 py-2 rounded-lg text-xs transition-all duration-200"
                  style={{
                    color:      'var(--text-dim)',
                    background: 'var(--bg3)',
                    border:     '1px solid var(--border)',
                    cursor:     deleting ? 'wait' : 'pointer',
                    fontFamily: 'Space Mono, monospace',
                  }}
                  title="Remove from history"
                >
                  Remove
                </button>
              </div>
            </div>
          )
        })}
      </div>
    </main>
  )
}
