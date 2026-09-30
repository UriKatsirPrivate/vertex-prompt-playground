# Development — Next.js + FastAPI rewrite

The modern UI lives in `frontend/` (Next.js 16 / React 19 / Tailwind v4 / shadcn-ui,
static export) and `backend/` (FastAPI wrapping the Vertex AI logic). The original
Streamlit app at the repo root still runs unchanged until the Phase 6 cutover.

## Local dev (two processes)

```bash
# 1. Backend (http://localhost:8000)
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/pip install --no-deps -r requirements-nodeps.txt
gcloud auth application-default login          # ADC for Vertex
.venv/bin/uvicorn app.main:app --reload --port 8000

# 2. Frontend (http://localhost:3000)
cd frontend
npm install
npm run dev      # uses .env.local -> NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

The backend allows CORS from `http://localhost:3000` in dev (see `PG_CORS_ORIGINS`).
First run downloads NLTK corpora for `gptrim` (Compress tool); if the auto-download
fails behind a proxy, run once:
`python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab')"`.

## Production shape (single container)

`next build` (output: export) → `frontend/out` → copied into the FastAPI image as
`backend/static`; FastAPI serves `/api/*` and the SPA from one Cloud Run service.
Verify locally:

```bash
cd frontend && npm run build
cp -r out ../backend/static
cd ../backend && .venv/bin/uvicorn app.main:app --port 8080
# http://localhost:8080  (UI)   http://localhost:8080/api/config  (API)
```

## Config (env vars, prefix `PG_`)

`PG_GCP_PROJECT_ID`, `PG_GCP_REGION`, `PG_DEFAULT_MODEL`, `PG_MODEL_NAMES`,
`PG_IMAGEN_MODEL`, `PG_CORS_ORIGINS`. Defaults mirror the old Streamlit app.

## Tests

```bash
cd backend && .venv/bin/python -m pytest tests/ -q     # offline (no Vertex)
cd frontend && npm run lint && npm run build            # type-check + lint + export
```

## Architecture notes

- Backend logic lives in `backend/app/core/` (no Streamlit). Tools are registered in
  `core/tools/__init__.py:TOOL_REGISTRY`; one generic endpoint `/api/tools/{id}` serves
  the 12 text/JSON tools. D.A.R.E and Images have dedicated endpoints (binary/multi-field).
- The frontend reads `/api/config` at runtime to build the grouped nav and forms.
  `GenericToolForm` drives 12 tools; only `dare` and `images` are bespoke pages.
- Static export must enumerate dynamic routes: generic tool ids are listed in
  `frontend/lib/tools.ts:GENERIC_TOOL_IDS` (mirror of the backend registry). Add a new
  generic tool there too, then rebuild.
