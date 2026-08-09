<div align="center">

# 🧪 MaterialMind AI

**An AI-powered engineering copilot for material selection**

*Built for the Reverie Hacks 2026  — Devpost*

[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![Tailwind](https://img.shields.io/badge/Styling-TailwindCSS-38B2AC?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](#license)

[Demo Video](#) · [Live Demo](#) · [Report a Bug](../../issues)

</div>

---

## The Problem

Choosing the right engineering material is one of the most consequential and most error-prone decisions in product design. Students and early-career engineers often default to familiar materials out of habit rather than fit, while trade-off data (strength, weight, cost, manufacturability, sustainability) is scattered across datasheets, standards, and institutional knowledge that isn't easy to search or compare.

## The Solution

**MaterialMind AI** is a conversational material selection copilot. You describe your application's real constraints temperature, environment, strength, weight priority, budget, quantity  and MaterialMind recommends a material with reasoning you can actually verify:

- ✅ **Verified database answers** are pulled from a hand-curated set of **72 engineering materials** with real, checkable numbers.
- 🤖 **AI-estimated answers**, used only when nothing in the database fits, are clearly labeled **"AI ESTIMATE verify before use"** so you're never misled into treating a guess as a fact.

Every recommendation is framed as a genuine trade-off, not a false "best" answer: top pick with an honest weakness, a runner-up, manufacturing considerations, and sustainability notes the way a senior materials engineer would actually explain a decision.

## Demo

> 🎥 *Add your Devpost demo video link here*

> 🖼️ *Here's screenshots: the wizard, a recommendation result, and the comparison view*
> <img width="1210" height="571" alt="Screenshot 2026-08-09 135333" src="https://github.com/user-attachments/assets/f2ae461d-aead-424a-8a6d-0f4024d46231" />
<img width="1225" height="630" alt="Screenshot 2026-08-09 140420" src="https://github.com/user-attachments/assets/9cb2ea5d-7d71-441d-8ca7-5e09fab48acb" />

> <img width="1056" height="629" alt="Screenshot 2026-08-09 141658" src="https://github.com/user-attachments/assets/33dcb410-cd68-4f89-bc7e-10ae3435c6be" />

## Key Features

| Feature | Description |
|---|---|
| 🧭 **Guided Wizard** | Step-by-step material selection based on real application constraints |
| 📚 **Verified Database + AI Fallback** | 72 verified materials, with transparent Gemini-powered estimates when nothing matches |
| ⚖️ **Material Comparison** | Side-by-side comparison of candidate materials |
| 🏭 **Manufacturing Advisor** | Suggests suitable manufacturing processes for the chosen material |
| 📄 **PDF Report Generation** | Downloadable engineering report summarizing the recommendation and reasoning |
| 🔍 **Browse & Search** | Explore the full verified material database directly |
| 📊 **Database Stats** | Quick overview of dataset coverage |

## How It Works

```
User answers wizard (application, temp, environment, strength, weight, budget, qty)
                │
                ▼
   Backend checks the 72-material verified database for a match
                │
        ┌───────┴────────┐
        ▼                ▼
   Match found      No match found
        │                │
        ▼                ▼
  Verified answer   Gemini generates a labeled
  with real data    AI estimate (trade-offs,
                     manufacturing, sustainability)
                │
                ▼
     Result shown in UI + optional PDF report
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Tailwind CSS |
| Backend | Python + FastAPI + Uvicorn |
| AI | Google Gemini API (`google-generativeai`, model `gemini-flash-latest`) |
| Data | `materials.csv` — 72 verified engineering materials |
| PDF Generation | ReportLab |

## Project Structure

```
Material-Mind-Ai/
├── materialmind-frontend/     # React + Vite + Tailwind frontend
│   └── src/
│       ├── components/        # Wizard, Recommendations, Comparison, Manufacturing, etc.
│       └── api.js             # Backend API client
└── MaterialMind-Backend-v2/   # FastAPI backend + Gemini integration
    ├── app_complete.py        # Main API application
    └── materials.csv          # Verified material database
```

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 18+
- [Python](https://www.python.org/) 3.10+
- A Google Gemini API key ([Google AI Studio](https://aistudio.google.com/))

### 1. Clone the repo

```bash
git clone https://github.com/abdulrehman-980/Material-Mind-Ai-.git
cd Material-Mind-Ai-
```

### 2. Backend setup

```bash
cd MaterialMind-Backend-v2
pip install -r requirements.txt
```

Set your Gemini API key as an environment variable:

**Windows (persists across sessions):**
```bash
setx GEMINI_API_KEY "your-key-here"
```
*(Close and reopen your terminal after running this once.)*

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your-key-here"
```

Run the backend:

```bash
python app_complete.py
```

Backend runs at `http://localhost:8080`.

### 3. Frontend setup

In a separate terminal:

```bash
cd materialmind-frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

> **Note:** Both servers must be running simultaneously, in separate terminal windows, for the app to function.

## Team

| Role | Contributor |
|---|---|
| Frontend, Integration & Testing | [Abdul](https://github.com/abdulrehman-980) |
| Backend & Material Database | NoHesiFactorial |

## Built For

**Reverie Hacks 2026** — [Devpost](https://devpost.com/)

## License

This project is licensed under the MIT License  see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<sub>Made with care for engineers who'd rather trust real data than guesswork.</sub>
</div>
