## Privacy Policy Analyzer (Weeks 1–3)

This repo contains:
- **Python analysis engine** (`analyzer/`) using spaCy + keyword patterns
- **Flask API** (`backend/`) exposing `/api/*` endpoints + SQLite cache
- **React frontend** (`frontend/`) built with Vite + Tailwind

### Prerequisites

- **Python 3.10+** (this project uses `str | None` type hints)
- **Node.js 18+** (recommended for Vite/React)

### Install (Windows PowerShell)

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Run (option A): Full web app (recommended)

Terminal 1 (backend):

```powershell
cd backend
python app.py
```

Terminal 2 (frontend):

```powershell
cd frontend
npm install
npm run dev
```

```powershell
cd frontend
npm run dev

Open `http://localhost:5173`.

### Run (option B): CLI only

From the project root:

```powershell
python main.py
```

Or analyze a specific URL:

```powershell
python main.py https://policies.google.com/privacy
```

Or re-run from a saved sentences file:

```powershell
python main.py --file policy_sentences.txt
```

### Notes / Troubleshooting

- **spaCy model missing**: run `python -m spacy download en_core_web_sm`
- **Frontend API calls**: `frontend/vite.config.js` proxies `/api` → `http://localhost:5000`
- **Cache DB**: `backend/analyzer_cache.db` is created automatically on first run

