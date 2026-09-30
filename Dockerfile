# syntax=docker/dockerfile:1
# Combined image for The Prompt Playground (Next.js + FastAPI).
# Stage 1 builds the static SPA; stage 2 is the FastAPI app that serves both
# /api/* and the static export from one Cloud Run service.

# ---- 1) Build the Next.js static export ----
FROM node:20-slim AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Production build is same-origin (/api). .dockerignore drops .env.local so the
# dev NEXT_PUBLIC_API_BASE_URL is not baked in.
RUN npm run build

# ---- 2) FastAPI app serving /api + the SPA ----
FROM python:3.12-slim AS api
ENV PYTHONUNBUFFERED=True \
    PYTHONDONTWRITEBYTECODE=1 \
    NLTK_DATA=/usr/share/nltk_data \
    PG_GCP_PROJECT_ID=landing-zone-demo-341118
WORKDIR /app
COPY backend/requirements.txt backend/requirements-nodeps.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --no-deps -r requirements-nodeps.txt \
    && python -m nltk.downloader -d /usr/share/nltk_data stopwords punkt punkt_tab
COPY backend/ ./
COPY --from=web /web/out ./static
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
