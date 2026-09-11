# The Prompt Playground

A playground for prompt-engineering techniques, powered by Google Vertex AI (Gemini for
text, Imagen for images). A **Next.js** single-page app talks to a **FastAPI** backend;
both ship in one container on **Google Cloud Run**.

## Features

- **Prompt-engineering tools:** fine-tune, system, agent, and meta prompts, and more.
- **Advanced techniques:** Zero-to-Few-Shot, Chain of Thought, D.A.R.E prompting.
- **Format generation:** JSON, Nano Banana JSON, and Veo prompts.
- **Image generation:** Imagen 4 from text descriptions.
- **Prompt compression** and per-tool **run history** (stored in your browser).
- **Live model config:** model, temperature, top-p, and token limits.

## Stack

- **Frontend:** Next.js 16 (App Router) · React 19 · Tailwind v4 · shadcn-ui · Zustand
  (static export)
- **Backend:** FastAPI · `google-genai` (Vertex AI) · `gptrim`
- **Deploy:** multi-stage Docker → Cloud Build → single Cloud Run service

## Prerequisites

- A Google Cloud project with the Vertex AI API enabled.
- `gcloud` CLI installed and authenticated (`gcloud auth application-default login`).
- Node 20+ and Python 3.12 for local development.

## Run locally

See **[DEVELOPMENT.md](./DEVELOPMENT.md)** for the full guide. Quick version (two processes):

```bash
# Backend  -> http://localhost:8000
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000

# Frontend -> http://localhost:3000
cd frontend && npm install && npm run dev
```

## Deploy

```bash
./deploy.sh
```

Builds the combined image via Cloud Build (`cloudbuild.yaml` + `Dockerfile`) and deploys
to Cloud Run. Configure the project/region/service variables at the top of `deploy.sh`.
The Cloud Run service account needs the **Vertex AI User** role. Runtime config is via
`PG_*` env vars (e.g. `PG_GCP_PROJECT_ID`, `PG_DEFAULT_MODEL`).

## Architecture

`Next.js SPA → /api/* (FastAPI) → core/ → Vertex AI`. The frontend reads `/api/config`
at runtime to build its grouped navigation and forms. Twelve of the fourteen tools are
served by one generic endpoint + form; D.A.R.E and Images are bespoke. See `CLAUDE.md`
for conventions.
