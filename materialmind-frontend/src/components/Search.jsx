import { useEffect, useState } from 'react'
import { api } from '../api'
import MaterialCard from './MaterialCard'

export default function Search({ onViewDetails }) {
  const [categories, setCategories] = useState([])
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [minStrength, setMinStrength] = useState('')
  const [maxDensity, setMaxDensity] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.categories().then((r) => setCategories(r.categories)).catch(() => {})
  }, [])

  async function runSearch(e) {
    e?.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await api.search({
        query,
        category: category || undefined,
        min_tensile_strength: minStrength ? Number(minStrength) : undefined,
        max_density: maxDensity ? Number(maxDensity) : undefined,
      })
      setResults(res)
    } catch (err) {
      setError(err.message || 'Search failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-14">
      <h2 className="font-display text-3xl font-medium text-paper mb-8">Browse materials</h2>

      <form onSubmit={runSearch} className="grid grid-cols-1 sm:grid-cols-4 gap-3 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search e.g. aluminum, titanium…"
          className="sm:col-span-2 bg-blueprint-900 border border-line focus:border-brass-500 rounded-lg px-4 py-2.5 text-paper placeholder:text-steel-400 font-body outline-none transition-colors"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-blueprint-900 border border-line focus:border-brass-500 rounded-lg px-4 py-2.5 text-paper font-mono text-sm outline-none transition-colors"
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={loading}
          className="bg-brass-500 hover:bg-copper-400 disabled:opacity-40 text-blueprint-950 font-display font-semibold px-5 py-2.5 rounded-lg transition-colors"
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      <div className="flex flex-wrap gap-4 mb-8 font-mono text-xs text-steel-300">
        <label className="flex items-center gap-2">
          min tensile (MPa)
          <input
            type="number"
            value={minStrength}
            onChange={(e) => setMinStrength(e.target.value)}
            className="w-24 bg-blueprint-900 border border-line focus:border-brass-500 rounded px-2 py-1 text-paper outline-none"
          />
        </label>
        <label className="flex items-center gap-2">
          max density (g/cm³)
          <input
            type="number"
            step="0.1"
            value={maxDensity}
            onChange={(e) => setMaxDensity(e.target.value)}
            className="w-24 bg-blueprint-900 border border-line focus:border-brass-500 rounded px-2 py-1 text-paper outline-none"
          />
        </label>
      </div>

      {error && <p className="font-mono text-sm text-rust-500 mb-6">{error}</p>}

      {results && (
        <>
          <p className="font-mono text-[10px] text-steel-400 uppercase tracking-widest mb-3">
            {results.count} results
          </p>
          {results.count === 0 ? (
            <p className="font-body text-steel-300">
              No materials matched. Try widening the filters or clearing the category.
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {results.results.map((m) => (
                <MaterialCard key={m.id} material={m} onViewDetails={onViewDetails} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
