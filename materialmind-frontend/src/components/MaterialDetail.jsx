import { useEffect, useState } from 'react'
import { api } from '../api'
import MaterialCard from './MaterialCard'

export default function MaterialDetail({ materialId, onBack }) {
  const [material, setMaterial] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    setMaterial(null)
    setError(null)
    api.material(materialId).then(setMaterial).catch((err) => setError(err.message))
  }, [materialId])

  return (
    <div className="mx-auto max-w-2xl px-6 py-14">
      <button
        onClick={onBack}
        className="font-mono text-xs uppercase tracking-widest text-steel-400 hover:text-paper transition-colors mb-8"
      >
        ← Back to browse
      </button>

      {error && <p className="font-mono text-sm text-rust-500">{error}</p>}

      {!error && !material && (
        <p className="font-mono text-sm text-steel-400">Loading spec sheet…</p>
      )}

      {material && (
        <>
          <MaterialCard material={material} />

          {(material.limitations || material.common_applications || material.manufacturing_methods) && (
            <div className="mt-6 flex flex-col gap-5">
              {material.common_applications && (
                <div>
                  <p className="font-mono text-[10px] text-brass-400 uppercase tracking-widest mb-1">
                    Common applications
                  </p>
                  <p className="font-body text-sm text-steel-300 leading-relaxed">
                    {material.common_applications}
                  </p>
                </div>
              )}
              {material.limitations && (
                <div>
                  <p className="font-mono text-[10px] text-brass-400 uppercase tracking-widest mb-1">
                    Limitations
                  </p>
                  <p className="font-body text-sm text-steel-300 leading-relaxed">
                    {material.limitations}
                  </p>
                </div>
              )}
              {material.manufacturing_methods && (
                <div>
                  <p className="font-mono text-[10px] text-brass-400 uppercase tracking-widest mb-1">
                    Manufacturing methods
                  </p>
                  <p className="font-body text-sm text-steel-300 leading-relaxed">
                    {material.manufacturing_methods}
                  </p>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
