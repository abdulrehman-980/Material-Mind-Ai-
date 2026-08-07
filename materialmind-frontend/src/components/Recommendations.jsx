import MaterialCard from './MaterialCard'

export default function Recommendations({
  data,
  selectedIds,
  onToggle,
  onCompare,
  onManufacturing,
  onReport,
  onStartOver,
  reportLoading,
}) {
  const canCompare = selectedIds.size >= 2
  const canReport = selectedIds.size >= 2

  return (
    <div className="mx-auto max-w-5xl px-6 py-14">
      <div className="flex items-start justify-between gap-6 mb-8">
        <div>
          <p className="font-mono text-xs text-steel-400 tracking-widest uppercase mb-2">
            {data.total_candidates} candidates found
            {!data.gemini_available && ' · AI reasoning unavailable, showing raw matches'}
          </p>
          <h2 className="font-display text-3xl font-medium text-paper">Recommendation</h2>
        </div>
        <button
          onClick={onStartOver}
          className="font-mono text-xs uppercase tracking-widest text-steel-400 hover:text-paper transition-colors shrink-0"
        >
          ← Start over
        </button>
      </div>

      {data.recommendation && (
        <div className="bg-blueprint-900 border border-line rounded-md p-6 mb-10">
          <p className="font-mono text-[10px] text-brass-400 uppercase tracking-widest mb-3">
            Engineering rationale
          </p>
          <p className="font-body text-paper leading-relaxed whitespace-pre-line">
            {data.recommendation}
          </p>
        </div>
      )}

      <p className="font-mono text-[10px] text-steel-400 uppercase tracking-widest mb-3">
        Select 2 or more to compare or generate a report
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-10">
        {data.candidates.map((m) => (
          <MaterialCard
            key={m.id}
            material={m}
            selectable
            selected={selectedIds.has(m.id)}
            onToggle={onToggle}
            onViewManufacturing={onManufacturing}
          />
        ))}
      </div>

      <div className="flex flex-wrap gap-3 border-t border-line pt-6">
        <button
          onClick={onCompare}
          disabled={!canCompare}
          className="bg-brass-500 hover:bg-copper-400 disabled:opacity-30 disabled:cursor-not-allowed text-blueprint-950 font-display font-semibold px-5 py-2.5 rounded-lg transition-colors"
        >
          Compare selected ({selectedIds.size})
        </button>
        <button
          onClick={onReport}
          disabled={!canReport || reportLoading}
          className="border border-brass-500 text-brass-400 hover:bg-brass-500/10 disabled:opacity-30 disabled:cursor-not-allowed font-display font-semibold px-5 py-2.5 rounded-lg transition-colors"
        >
          {reportLoading ? 'Generating PDF…' : 'Generate PDF report'}
        </button>
      </div>
    </div>
  )
}
