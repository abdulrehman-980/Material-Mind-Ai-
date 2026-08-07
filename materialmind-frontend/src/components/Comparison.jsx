export default function Comparison({ data, onBack, onReport, reportLoading }) {
  const materialNames = data.materials.map((m) => m.material_name)

  return (
    <div className="mx-auto max-w-5xl px-6 py-14">
      <div className="flex items-start justify-between gap-6 mb-8">
        <div>
          <p className="font-mono text-xs text-steel-400 tracking-widest uppercase mb-2">
            {data.materials.length} materials
          </p>
          <h2 className="font-display text-3xl font-medium text-paper">Comparison</h2>
        </div>
        <button
          onClick={onBack}
          className="font-mono text-xs uppercase tracking-widest text-steel-400 hover:text-paper transition-colors shrink-0"
        >
          ← Back to results
        </button>
      </div>

      <div className="overflow-x-auto border border-line rounded-md mb-8">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-line bg-blueprint-900">
              <th className="text-left font-mono text-[10px] text-steel-400 uppercase tracking-widest px-4 py-3">
                Property
              </th>
              {materialNames.map((name) => (
                <th
                  key={name}
                  className="text-left font-display text-sm font-medium text-paper px-4 py-3 whitespace-nowrap"
                >
                  {name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.comparison_table.map((row, idx) => (
              <tr key={row.property} className={idx % 2 ? 'bg-blueprint-900/40' : ''}>
                <td className="font-mono text-xs text-steel-400 px-4 py-3 border-t border-line whitespace-nowrap">
                  {row.property}
                </td>
                {materialNames.map((name) => (
                  <td
                    key={name}
                    className="font-mono text-sm text-paper px-4 py-3 border-t border-line"
                  >
                    {row[name] ?? 'N/A'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button
        onClick={onReport}
        disabled={reportLoading}
        className="border border-brass-500 text-brass-400 hover:bg-brass-500/10 disabled:opacity-30 font-display font-semibold px-5 py-2.5 rounded-lg transition-colors"
      >
        {reportLoading ? 'Generating PDF…' : 'Generate PDF report'}
      </button>
    </div>
  )
}
