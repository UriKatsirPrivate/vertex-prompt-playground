# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

**The Prompt Playground** — a web app exposing a suite of prompt-engineering tools
backed by Google Vertex AI (Gemini for text, Imagen for images). A Next.js SPA frontend
talks to a FastAPI backend; both ship in one container on Google Cloud Run.

> History: this was originally a single-file Streamlit app. It was rewritten to
> Next.js + FastAPI (see `DEVELOPMENT.md`). The last Streamlit commit is tagged
> `streamlit-final` for rollback.

## Tech stack

- **Frontend:** Next.js 16 (App Router) · React 19 · Tailwind v4 · shadcn-ui
  (which uses **Base UI**, not Radix) · Zustand · next-themes. Built as a **static
  export** (`output: "export"`).
- **Backend:** FastAPI · `google-genai` SDK (Vertex AI) · `gptrim` ·
  Pydantic v2 / pydantic-settings. Python 3.12.
- **Deploy:** multi-stage `Dockerfile` → Cloud Build → single Cloud Run service.

## Layout

```
backend/app/
  main.py            # FastAPI app: /api router + serves the SPA from ./static
  config.py          # Settings (env prefix PG_); safety in core/safety.py
  deps.py            # build_context() -> ToolContext
  core/
    client.py        # cached genai.Client (lru_cache, replaces st.cache_resource)
    generation.py    # generate_text(); typed errors (errors.py), no st.*
    tools/__init__.py# TOOL_REGISTRY: id -> ToolSpec (the registry IS the API surface)
    tools/{text_tools,json_tools,dare,images,compress}.py
    prompts/         # prompt templates (system_prompts, *_prompt, placeholders)
  api/{routes_tools,routes_config,schemas}.py
frontend/
  app/(tools)/[toolId]/page.tsx   # generic tool page (static-generated per id)
  app/(tools)/{dare,images}/page.tsx  # the 2 bespoke tools
  components/  lib/{api,types,history,tools}.ts  store/config-store.ts
```

## Key conventions

- **One generic path for most tools.** 12 of 14 tools are "text/JSON in → blocks out",
  served by `POST /api/tools/{id}` and rendered by `GenericToolForm`. Only **D.A.R.E**
  (multi-field) and **Images** (binary) have dedicated endpoints + pages.
- **Adding a tool:** add a handler + `ToolSpec` to `backend/app/core/tools/` (registry),
  then add its id to `frontend/lib/tools.ts:GENERIC_TOOL_IDS` (static export must
  enumerate dynamic routes) and rebuild. Nav/forms come from `/api/config` automatically.
- **No Streamlit, no `st.*` in the backend.** Logic lives in `core/`; errors are raised
  as typed `PlaygroundError`s and mapped to HTTP in `main.py`.
- **Model path:** `projects/{project}/locations/{region}/publishers/google/models/{model}`.
- **Config via env (prefix `PG_`):** `PG_GCP_PROJECT_ID`, `PG_GCP_REGION` (default
  `global`), `PG_DEFAULT_MODEL`, `PG_MODEL_NAMES`, `PG_IMAGEN_MODEL`, `PG_CORS_ORIGINS`.
- **Model config** (model + temp/top-p/max-tokens) is client state (Zustand, persisted)
  sent with every request as `modelConfig`; no server session state, no server LLM cache
  (frontend localStorage history replaces the old `@st.cache_data`).
- **shadcn here is Base UI:** compose with the `render` prop, not `asChild`.

## Tools

Fine-Tune · System · Agent · Meta · Zero-to-Few · Chain-of-Thought · Json ·
Nano Banana · Veo · Run · Compress (generic) + D.A.R.E · Images (bespoke).

## Run & deploy

See **`DEVELOPMENT.md`** for the full local two-process setup and the prod single-
container build. Quick version:

```bash
# backend
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
# frontend
cd frontend && npm install && npm run dev      # :3000 -> :8000 via .env.local

# tests
cd backend && .venv/bin/python -m pytest tests/ -q
cd frontend && npm run lint && npm run build
```

Deploy: `./deploy.sh` (Cloud Build via `cloudbuild.yaml` + `Dockerfile`, deploys to
Cloud Run; SA needs **Vertex AI User**). gptrim needs NLTK corpora (the Dockerfile
downloads `stopwords`/`punkt`/`punkt_tab`); `pyOpenSSL` is required for google-auth.

## Notes

- Imagen model is `imagen-4.0-fast-generate-001` (`PG_IMAGEN_MODEL` /
  `core/tools/images.py`).
- `analysis_and_enhancement.py` at the repo root is an unused leftover prompt template
  (not imported anywhere) — safe to delete.
