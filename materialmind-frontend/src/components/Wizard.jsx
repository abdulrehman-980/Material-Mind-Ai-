import { useState } from 'react'

const STEPS = [
  { key: 'application', label: 'Application', type: 'text' },
  { key: 'temperature', label: 'Operating temperature', type: 'choice',
    options: ['Ambient (< 60°C)', 'Elevated (60–300°C)', 'High (300–800°C)', 'Extreme (> 800°C)'] },
  { key: 'environment', label: 'Environment', type: 'choice',
    options: ['Indoor / dry', 'Outdoor / weathering', 'Marine / saline', 'Chemical / corrosive'] },
  { key: 'strength', label: 'Strength requirement', type: 'choice',
    options: ['Low', 'Medium', 'High', 'Very high (fatigue-critical)'] },
  { key: 'weight', label: 'Weight priority', type: 'choice',
    options: ['Not a priority', 'Moderate', 'Lightweight critical'] },
  { key: 'budget', label: 'Budget', type: 'choice',
    options: ['Low', 'Medium', 'High'] },
  { key: 'quantity', label: 'Production quantity', type: 'number', placeholder: 'e.g. 500 units' },
]

const initial = {
  application: '',
  temperature: '',
  environment: '',
  strength: '',
  weight: '',
  budget: '',
  quantity: '',
  sustainability_priority: false,
}

export default function Wizard({ onSubmit, loading }) {
  const [i, setI] = useState(0)
  const [data, setData] = useState(initial)

  const step = STEPS[i]
  const isLast = i === STEPS.length - 1
  const value = data[step.key]
  const canAdvance = step.type === 'number' ? true : value !== ''

  function set(key, val) {
    setData((d) => ({ ...d, [key]: val }))
  }

  function next() {
    if (isLast) {
      const payload = {
        application: data.application || 'general engineering component',
        requirements: {
          temperature: data.temperature,
          environment: data.environment,
          strength: data.strength,
          weight: data.weight,
        },
        budget: data.budget.toLowerCase() || undefined,
        sustainability_priority: data.sustainability_priority,
        quantity: data.quantity ? Number(data.quantity) : 100,
      }
      onSubmit(payload)
      return
    }
    setI((n) => n + 1)
  }

  function back() {
    setI((n) => Math.max(0, n - 1))
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-14">
      {/* progress ticks — blueprint measurement marks, not decorative numbering */}
      <div className="flex gap-1.5 mb-10">
        {STEPS.map((s, idx) => (
          <div
            key={s.key}
            className={`h-1 flex-1 rounded-full transition-colors ${
              idx <= i ? 'bg-brass-500' : 'bg-line'
            }`}
          />
        ))}
      </div>

      <p className="font-mono text-xs text-steel-400 tracking-widest uppercase mb-2">
        Step {i + 1} of {STEPS.length}
      </p>
      <h2 className="font-display text-3xl font-medium text-paper mb-8">
        {step.label}
      </h2>

      {step.type === 'text' && (
        <input
          autoFocus
          type="text"
          value={value}
          onChange={(e) => set(step.key, e.target.value)}
          placeholder="e.g. lightweight bracket for an EV suspension arm"
          className="w-full bg-blueprint-900 border border-line focus:border-brass-500 rounded-lg px-4 py-3 text-paper placeholder:text-steel-400 font-body outline-none transition-colors"
          onKeyDown={(e) => e.key === 'Enter' && canAdvance && next()}
        />
      )}

      {step.type === 'number' && (
        <input
          autoFocus
          type="number"
          min="1"
          value={value}
          onChange={(e) => set(step.key, e.target.value)}
          placeholder={step.placeholder}
          className="w-full bg-blueprint-900 border border-line focus:border-brass-500 rounded-lg px-4 py-3 text-paper placeholder:text-steel-400 font-mono outline-none transition-colors"
          onKeyDown={(e) => e.key === 'Enter' && next()}
        />
      )}

      {step.type === 'choice' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {step.options.map((opt) => (
            <button
              key={opt}
              onClick={() => set(step.key, opt)}
              className={`text-left px-4 py-3 rounded-lg border font-body transition-colors ${
                value === opt
                  ? 'border-brass-500 bg-brass-500/10 text-paper'
                  : 'border-line bg-blueprint-900 text-steel-300 hover:border-steel-400'
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      )}

      {isLast && (
        <label className="flex items-center gap-2 mt-6 font-mono text-xs text-steel-300">
          <input
            type="checkbox"
            checked={data.sustainability_priority}
            onChange={(e) => set('sustainability_priority', e.target.checked)}
            className="accent-brass-500"
          />
          Prioritize sustainability / recyclability
        </label>
      )}

      <div className="flex items-center justify-between mt-10">
        <button
          onClick={back}
          disabled={i === 0}
          className="font-mono text-xs uppercase tracking-widest text-steel-400 disabled:opacity-0 hover:text-paper transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={next}
          disabled={!canAdvance || loading}
          className="bg-brass-500 hover:bg-copper-400 disabled:opacity-40 disabled:cursor-not-allowed text-blueprint-950 font-display font-semibold px-6 py-2.5 rounded-lg transition-colors"
        >
          {loading ? 'Analyzing…' : isLast ? 'Get recommendation' : 'Next →'}
        </button>
      </div>
    </div>
  )
}
