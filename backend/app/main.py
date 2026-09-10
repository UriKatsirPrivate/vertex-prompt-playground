"""FastAPI application entry point.

Serves the JSON API under ``/api`` and, in the production single-container build,
the Next.js static export under ``/``.
"""
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api import routes_config, routes_tools
from app.config import get_settings
from app.core.errors import PlaygroundError

settings = get_settings()

app = FastAPI(title="The Prompt Playground API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PlaygroundError)
async def playground_error_handler(_request: Request, exc: PlaygroundError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status,
        content={"detail": str(exc), "code": exc.code},
    )


app.include_router(routes_config.router, prefix="/api")
app.include_router(routes_tools.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# --- Static SPA (production single-container build) ---
# Registered last so /api/* always wins. Unknown non-API paths fall back to
# index.html so client-side routing works on refresh/deep-link. When the static
# export is absent (local dev), the API runs on its own and the Next dev server
# serves the UI.
_static_dir = settings.static_dir
_static_dir_real = os.path.realpath(_static_dir)
if os.path.isdir(_static_dir):

    def _safe_static_path(full_path: str) -> str | None:
        """Resolve ``full_path`` under ``_static_dir``, rejecting traversal outside it."""
        candidate = os.path.realpath(os.path.join(_static_dir_real, full_path))
        if os.path.commonpath([_static_dir_real, candidate]) != _static_dir_real:
            return None
        return candidate

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not found", "code": "not_found"})

        candidate = _safe_static_path(full_path)
        if candidate is None:
            return JSONResponse(status_code=404, content={"detail": "Not found", "code": "not_found"})

        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        # Static export emits /fine_tune.html for the /fine_tune route — serve the
        # prerendered page for deep-links/refreshes.
        html_candidate = f"{candidate}.html"
        if full_path and os.path.isfile(html_candidate):
            return FileResponse(html_candidate)
        index = os.path.join(_static_dir_real, "index.html")
        if os.path.isfile(index):
            return FileResponse(index)
        return JSONResponse(status_code=404, content={"detail": "Not found", "code": "not_found"})
