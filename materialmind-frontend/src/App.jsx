import { useState } from 'react'
import { api, ApiError } from './api'
import Header from './components/Header'
import Wizard from './components/Wizard'
import Recommendations from './components/Recommendations'
import Comparison from './components/Comparison'
import Manufacturing from './components/Manufacturing'
import Search from './components/Search'
import MaterialDetail from './components/MaterialDetail'
import Stats from './components/Stats'
import ErrorBanner from './components/ErrorBanner'

export default function App() {
  const [tab, setTab] = useState('assistant') // assistant | browse | stats
  const [browseDetailId, setBrowseDetailId] = useState(null)

  const [view, setView] = useState('wizard') // wizard | recommend | compare | manufacturing
  const [loading, setLoading] = useState(false)
  const [reportLoading, setReportLoading] = useState(false)
  const [error, setError] = useState(null)

  const [quantity, setQuantity] = useState(100)
  const [recommendData, setRecommendData] = useState(null)
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [compareData, setCompareData] = useState(null)
  const [manufacturingData, setManufacturingData] = useState(null)

  function fail(err) {
    setError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.')
  }

  async function handleWizardSubmit(payload) {
    setLoading(true)
    setError(null)
    setQuantity(payload.quantity)
    try {
      const { quantity: _q, ...recommendPayload } = payload
      const res = await api.recommend(recommendPayload)
      if (res.status === 'error') {
        setError(res.message || 'No materials matched those requirements.')
        return
      }
      setRecommendData(res)
      setSelectedIds(new Set())
      setView('recommend')
    } catch (err) {
      fail(err)
    } finally {
      setLoading(false)
    }
  }

  function toggleSelect(id) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  async function handleCompare() {
    setLoading(true)
    setError(null)
    try {
      const res = await api.compare({ material_ids: [...selectedIds] })
      setCompareData(res)
      setView('compare')
    } catch (err) {
      fail(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleManufacturing(materialId) {
    setLoading(true)
    setError(null)
    try {
      const res = await api.manufacturing({ material_id: materialId, quantity })
      setManufacturingData(res)
      setView('manufacturing')
    } catch (err) {
      fail(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleReport() {
    setReportLoading(true)
    setError(null)
    try {
      const { blob, filename } = await api.report({ material_ids: [...selectedIds] })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      fail(err)
    } finally {
      setReportLoading(false)
    }
  }

  function startOver() {
    setView('wizard')
    setRecommendData(null)
    setCompareData(null)
    setManufacturingData(null)
    setSelectedIds(new Set())
  }

  const stepLabel = {
    wizard: 'Material selection wizard',
    recommend: 'Recommendation',
    compare: 'Comparison',
    manufacturing: 'Manufacturing advisor',
  }[view]

  return (
    <div className="min-h-screen">
      <Header
        step={stepLabel}
        tab={tab}
        onTabChange={(t) => {
          setTab(t)
          setBrowseDetailId(null)
        }}
      />
      <ErrorBanner message={error} onDismiss={() => setError(null)} />

      {tab === 'assistant' && (
        <>
          {view === 'wizard' && <Wizard onSubmit={handleWizardSubmit} loading={loading} />}

          {view === 'recommend' && recommendData && (
            <Recommendations
              data={recommendData}
              selectedIds={selectedIds}
              onToggle={toggleSelect}
              onCompare={handleCompare}
              onManufacturing={handleManufacturing}
              onReport={handleReport}
              onStartOver={startOver}
              reportLoading={reportLoading}
            />
          )}

          {view === 'compare' && compareData && (
            <Comparison
              data={compareData}
              onBack={() => setView('recommend')}
              onReport={handleReport}
              reportLoading={reportLoading}
            />
          )}

          {view === 'manufacturing' && manufacturingData && (
            <Manufacturing data={manufacturingData} onBack={() => setView('recommend')} />
          )}
        </>
      )}

      {tab === 'browse' &&
        (browseDetailId ? (
          <MaterialDetail materialId={browseDetailId} onBack={() => setBrowseDetailId(null)} />
        ) : (
          <Search onViewDetails={setBrowseDetailId} />
        ))}

      {tab === 'stats' && <Stats />}
    </div>
  )
}
