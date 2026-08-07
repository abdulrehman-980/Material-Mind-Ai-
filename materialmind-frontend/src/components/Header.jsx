import { useEffect, useState } from 'react'
import { api } from '../api'

const TABS = [
  { key: 'assistant', label: 'Assistant' },
  { key: 'browse', label: 'Browse' },
  { key: 'stats', label: 'Stats' },
]

export default function Header({ step, tab, onTabChange }) {
  const [status, setStatus] = useState('checking') // checking | live | offline

  useEffect(() => {
    let cancelled = false
    async function check() {
      try {
        await api.health()
        if (!cancelled) setStatus('live')
      } catch {
        if (!cancelled) setStatus('offline')
      }
    }
    check()
    const id = setInterval(check, 30000)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  const dot =
    status === 'live'
      ? 'bg-alloy-green'
      : status === 'offline'
      ? 'bg-rust-500'
      : 'bg-steel-400'

  const label =
    status === 'live' ? 'API online' : status === 'offline' ? 'API unreachable' : 'checking…'

  return (
    <header className="border-b border-line/60">
      <div className="mx-auto max-w-5xl px-6 py-6 flex items-center justify-between">
        <div>
          <div className="flex items-baseline gap-3">
            <h1 className="font-display text-2xl font-semibold tracking-tight text-paper">
              MaterialMind
            </h1>
            <span className="font-mono text-[11px] text-steel-400 tracking-widest uppercase">
              v2.0
            </span>
          </div>
          <p className="font-mono text-xs text-steel-300 mt-1">
            engineering decision assistant — material selection &amp; process advisory
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs text-steel-300">
          <span className={`inline-block w-2 h-2 rounded-full ${dot}`} />
          {label}
        </div>
      </div>

      <div className="mx-auto max-w-5xl px-6 pb-4 flex items-center justify-between">
        <nav className="flex gap-1">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => onTabChange(t.key)}
              className={`font-mono text-xs uppercase tracking-widest px-3 py-1.5 rounded-full transition-colors ${
                tab === t.key
                  ? 'bg-brass-500/15 text-brass-400 border border-brass-500/50'
                  : 'text-steel-400 border border-transparent hover:text-paper'
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
        {step && tab === 'assistant' && (
          <span className="font-mono text-[11px] text-steel-400 tracking-widest uppercase">
            {step}
          </span>
        )}
      </div>
    </header>
  )
}
