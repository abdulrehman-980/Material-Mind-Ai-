# MaterialMind — Frontend

React + Tailwind frontend for the MaterialMind engineering decision assistant, built against
the FastAPI backend endpoints your teammate shared.

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

Runs at `http://localhost:5173`. Make sure the FastAPI backend is running on
`http://localhost:8000` (or update `VITE_API_BASE_URL` in `.env` to match).

If the backend has CORS locked down to specific origins rather than `"*"`, make sure
`http://localhost:5173` is allowed.

## How it maps to the backend

| Screen | Endpoint |
|---|---|
| Wizard → submit | `POST /materials/recommend` |
| Recommendation results | (uses the response above) |
| Compare selected materials | `POST /materials/compare` |
| Manufacturing advisor | `POST /materials/manufacturing` |
| Generate PDF report | `POST /materials/report` (downloads the returned file) |
| Header status dot | `GET /health`, polled every 30s |

The wizard's 7 questions (application, temperature, environment, strength, weight, budget,
quantity) map into the backend's `RecommendationRequest` shape:

```json
{
  "application": "string",
  "requirements": { "temperature": "...", "environment": "...", "strength": "...", "weight": "..." },
  "budget": "low | medium | high",
  "sustainability_priority": true
}
```

Quantity isn't part of `/materials/recommend` — it's held in state and sent later to
`/materials/manufacturing` when you drill into a specific material.

## Still open / to confirm with your teammate

- **API key header**: he mentioned the backend requires an API key it uses internally for
  Gemini — that should stay server-side and the frontend shouldn't need to send anything.
  But if he's added a client-facing auth header, set `VITE_API_KEY` in `.env` and confirm the
  exact header name in `src/api.js` (`headers()` function).
- **Deployment**: once the backend moves from localhost to Render, update
  `VITE_API_BASE_URL` (in Vercel's env var settings for the deployed frontend).

## Structure

```
src/
  api.js                     — all fetch calls, typed to match the backend schemas
  App.jsx                    — view state + orchestration
  components/
    Header.jsx                — title + live API status
    Wizard.jsx                 — 7-step material selection form
    MaterialCard.jsx           — spec-sheet style material card (used throughout)
    Recommendations.jsx        — AI reasoning + candidate grid
    Comparison.jsx             — side-by-side comparison table
    Manufacturing.jsx          — process advice for a selected material
    ErrorBanner.jsx             — shared error display
```
