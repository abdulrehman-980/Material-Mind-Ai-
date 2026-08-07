// API layer for the MaterialMind FastAPI backend.
//
// Base URL: reads from VITE_API_BASE_URL (see .env.example). Defaults to
// localhost:8000 since that's where the backend is currently running.
//
// If your backend ends up requiring a client-side API key header (separate
// from the Gemini key it holds server-side), set VITE_API_KEY in .env and
// uncomment the header line below — ask your teammate what header name the
// backend expects (e.g. "x-api-key").

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_KEY = import.meta.env.VITE_API_KEY

function headers(json = true) {
  const h = {}
  if (json) h['Content-Type'] = 'application/json'
  if (API_KEY) h['x-api-key'] = API_KEY // adjust header name if teammate specifies a different one
  return h
}

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(`${BASE_URL}${path}`, options)
  } catch (err) {
    throw new ApiError(
      `Couldn't reach the API at ${BASE_URL}. Is the backend running?`,
      0
    )
  }
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      /* ignore parse failure */
    }
    throw new ApiError(detail, res.status)
  }
  return res
}

export const api = {
  health: () => request('/health').then((r) => r.json()),

  categories: () => request('/categories').then((r) => r.json()),

  stats: () => request('/materials/stats').then((r) => r.json()),

  material: (id) => request(`/materials/${id}`).then((r) => r.json()),

  search: (payload) =>
    request('/materials/search', {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ limit: 20, ...payload }),
    }).then((r) => r.json()),

  // payload: { application, requirements: {strength, weight, temperature, environment},
  //            budget, sustainability_priority }
  recommend: (payload) =>
    request('/materials/recommend', {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify(payload),
    }).then((r) => r.json()),

  // payload: { material_ids: number[], focus }
  compare: (payload) =>
    request('/materials/compare', {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ focus: 'all', ...payload }),
    }).then((r) => r.json()),

  // payload: { material_id, quantity, desired_processes, budget_priority }
  manufacturing: (payload) =>
    request('/materials/manufacturing', {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ budget_priority: 'balanced', ...payload }),
    }).then((r) => r.json()),

  // payload: { material_ids, report_title, include_gemini_analysis }
  // Returns a Blob (PDF) rather than JSON, since the backend streams a file.
  report: async (payload) => {
    const res = await request('/materials/report', {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({
        report_title: 'Material Comparison Report',
        include_gemini_analysis: true,
        ...payload,
      }),
    })
    const blob = await res.blob()
    const disposition = res.headers.get('Content-Disposition') || ''
    const match = disposition.match(/filename=([^;]+)/)
    const filename = match ? match[1].trim() : 'material_comparison.pdf'
    return { blob, filename }
  },
}

export { ApiError }
