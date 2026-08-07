import { useEffect, useState } from 'react'
import { api } from '../api'

function Metric({ label, value }) {
  return (
    <div className="bg-blueprint-900 border border-line rounded-md p-5">
      <p className="font-mono text-[10px] text-steel-400 uppercase tracking-widest mb-2">
        {label}
      </p>
      <p className="font-display text-2xl text-paper">{value}</p>
    </div>
  )
}

export default function Stats() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.stats().then(setStats).catch((err) => setError(err.message))
  }, [])

  const byCategory = stats?.materials_by_category
    ? Object.entries(stats.materials_by_category).sort((a, b) => b[1] - a[1])
    : []
  const maxCount = byCategory.length ? byCategory[0][1] : 1

  return (
    <div className="mx-auto max-w-4xl px-6 py-14">
      <h2 className="font-display text-3xl font-medium text-paper mb-8">Database stats</h2>

      {error && <p className="font-mono text-sm text-rust-500">{error}</p>}
      {!error && !stats && <p className="font-mono text-sm text-steel-400">Loading…</p>}

      {stats && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
            <Metric label="Total materials" value={stats.total} />
            <Metric label="Categories" value={stats.categories} />
            <Metric
              label="Avg tensile strength"
              value={`${Math.round(stats.avg_tensile_strength_mpa)} MPa`}
            />
            <Metric label="Avg density" value={`${stats.avg_density_g_cm3?.toFixed(2)} g/cm³`} />
          </div>

          {byCategory.length > 0 && (
            <div>
              <p className="font-mono text-[10px] text-brass-400 uppercase tracking-widest mb-4">
                Materials by category
              </p>
              <div className="flex flex-col gap-2.5">
                {byCategory.map(([name, count]) => (
                  <div key={name} className="flex items-center gap-3">
                    <span className="font-mono text-xs text-steel-300 w-40 truncate">{name}</span>
                    <div className="flex-1 bg-blueprint-900 rounded-sm h-4 overflow-hidden">
                      <div
                        className="bg-brass-500 h-full rounded-sm"
                        style={{ width: `${(count / maxCount) * 100}%` }}
                      />
                    </div>
                    <span className="font-mono text-xs text-paper w-6 text-right">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
