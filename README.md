\# MaterialMind AI



\*\*AI-powered engineering material selection assistant — built for the Gemini XPrice Hackathon (Devpost)\*\*



MaterialMind helps engineers and students choose the right material for a given application. Answer a short guided wizard (application, temperature, environment, strength requirement, weight priority, budget, and quantity), and the system recommends materials either from a verified 72-material database or, when nothing in the database matches, from Gemini's general knowledge — clearly labeled as an AI estimate so you always know how trustworthy a recommendation is.



\## Features



\- \*\*Guided recommendation wizard\*\* — step-by-step material selection based on real engineering constraints

\- \*\*Verified database + AI fallback\*\* — 72 hand-verified materials, with a Gemini-powered estimate (clearly labeled) when nothing matches

\- \*\*Material comparison\*\* — side-by-side comparison of candidate materials

\- \*\*Manufacturing process advisor\*\* — suggests suitable manufacturing processes for the recommended material

\- \*\*PDF report generation\*\* — downloadable engineering report summarizing the recommendation and reasoning

\- \*\*Browse \& search\*\* — explore the full verified material database directly

\- \*\*Database stats\*\* — overview of the dataset



\## Tech Stack



| Layer | Technology |

|---|---|

| Frontend | React + Vite + Tailwind CSS |

| Backend | Python + FastAPI + Uvicorn |

| AI | Google Gemini API (`google-generativeai`, model `gemini-flash-latest`) |

| Data | `materials.csv` — 72 verified engineering materials |

| PDF generation | ReportLab |



\## Project Structure



```

Material-Mind-Ai/

├── materialmind-frontend/     # React + Vite + Tailwind frontend

└── MaterialMind-Backend-v2/   # FastAPI backend + Gemini integration

```



\## Getting Started



\### Prerequisites



\- \[Node.js](https://nodejs.org/) (for the frontend)

\- \[Python 3.x](https://www.python.org/) (for the backend)

\- A Google Gemini API key (\[Google AI Studio](https://aistudio.google.com/))



\### 1. Clone the repo



```bash

git clone https://github.com/abdulrehman-980/Material-Mind-Ai-.git

cd Material-Mind-Ai-

```



\### 2. Backend setup



```bash

cd MaterialMind-Backend-v2

pip install -r requirements.txt

```



Set your Gemini API key as an environment variable:



\*\*Windows (persists across sessions):\*\*

```bash

setx GEMINI\_API\_KEY "your-key-here"

```

\*(Close and reopen your terminal after running this once.)\*



\*\*macOS/Linux:\*\*

```bash

export GEMINI\_API\_KEY="your-key-here"

```



Run the backend:



```bash

python app\_complete.py

```



The backend runs at `http://localhost:8080`.



\### 3. Frontend setup



In a separate terminal:



```bash

cd materialmind-frontend

npm install

npm run dev

```



The frontend runs at `http://localhost:5173`.



> \*\*Note:\*\* Both the frontend and backend servers need to be running at the same time, in separate terminal windows, for the app to work.



\## Team



\- \*\*Frontend, integration \& testing:\*\* \[Abdul](https://github.com/abdulrehman-980)

\- \*\*Backend \& material database:\*\* NoHesiFactorial



\## Hackathon



Built for the \*\*Gemini XPrice Hackathon\*\* on Devpost.

