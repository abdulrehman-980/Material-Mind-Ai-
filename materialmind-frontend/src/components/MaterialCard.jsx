function Stat({ symbol, label, value, unit }) {
  if (value === undefined || value === null || value === '') return null
  return (
    <div>
      <div className="font-mono text-[10px] text-steel-400 uppercase tracking-wide">
        {symbol} {label}
      </div>
      <div className="font-mono text-sm text-paper">
        {value}
        {unit && <span className="text-steel-400"> {unit}</span>}
      </div>
    </div>
  )
}

export default function MaterialCard({
  material: m,
  selectable,
  selected,
  onToggle,
  onViewManufacturing,
  onViewDetails,
}) {
  return (
    <div
      className={`spec-corners bg-blueprint-900 border rounded-md p-5 flex flex-col gap-4 transition-colors ${
        selected ? 'border-brass-500' : 'border-line'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-mono text-[10px] text-steel-400 uppercase tracking-widest">
            {m.category}
          </p>
          <h3 className="font-display text-lg font-medium text-paper leading-snug">
            {m.material_name}
          </h3>
        </div>
        {selectable && (
          <input
            type="checkbox"
            checked={!!selected}
            onChange={() => onToggle(m.id)}
            className="mt-1 accent-brass-500 w-4 h-4 shrink-0"
            aria-label={`Select ${m.material_name} for comparison`}
          />
        )}
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-3">
        <Stat symbol="ρ" label="density" value={m.density_g_cm3} unit="g/cm³" />
        <Stat symbol="σᵤ" label="tensile" value={m.tensile_strength_mpa} unit="MPa" />
        <Stat symbol="σᵧ" label="yield" value={m.yield_strength_mpa} unit="MPa" />
        <Stat symbol="E" label="modulus" value={m.youngs_modulus_gpa} unit="GPa" />
        <Stat symbol="T" label="max temp" value={m.max_service_temp_c} unit="°C" />
        <Stat symbol="$" label="cost" value={m.cost} />
      </div>

      {m.advantages && (
        <p className="font-body text-sm text-steel-300 leading-relaxed border-t border-line pt-3">
          {m.advantages}
        </p>
      )}

      {(onViewManufacturing || onViewDetails) && (
        <div className="flex gap-4">
          {onViewDetails && (
            <button
              onClick={() => onViewDetails(m.id)}
              className="self-start font-mono text-[11px] uppercase tracking-widest text-brass-400 hover:text-copper-400 transition-colors"
            >
              View details →
            </button>
          )}
          {onViewManufacturing && (
            <button
              onClick={() => onViewManufacturing(m.id)}
              className="self-start font-mono text-[11px] uppercase tracking-widest text-brass-400 hover:text-copper-400 transition-colors"
            >
              Manufacturing advisor →
            </button>
          )}
        </div>
      )}
    </div>
  )
}
