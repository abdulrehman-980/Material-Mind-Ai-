export default function Manufacturing({ data, onBack }) {
  const methods = (data.recommended_methods || '')
    .split(';')
    .map((s) => s.trim())
    .filter(Boolean)

  return (
    <div className="mx-auto max-w-3xl px-6 py-14">
      <div className="flex items-start justify-between gap-6 mb-8">
        <div>
          <p className="font-mono text-xs text-steel-400 tracking-widest uppercase mb-2">
            {data.material.category}
            {!data.gemini_available && ' · AI reasoning unavailable'}
          </p>
          <h2 className="font-display text-3xl font-medium text-paper">
            {data.material.material_name}
          </h2>
        </div>
        <button
          onClick={onBack}
          className="font-mono text-xs uppercase tracking-widest text-steel-400 hover:text-paper transition-colors shrink-0"
        >
          ← Back
        </button>
      </div>

      {methods.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-8">
          {methods.map((method) => (
            <span
              key={method}
              className="font-mono text-xs text-brass-400 border border-brass-500/50 rounded-full px-3 py-1"
            >
              {method}
            </span>
          ))}
        </div>
      )}

      <div className="bg-blueprint-900 border border-line rounded-md p-6">
        <p className="font-mono text-[10px] text-brass-400 uppercase tracking-widest mb-3">
          Process guidance
        </p>
        <p className="font-body text-paper leading-relaxed whitespace-pre-line">{data.advice}</p>
      </div>
    </div>
  )
}
